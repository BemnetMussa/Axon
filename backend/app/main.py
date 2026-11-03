import os
import sys
import asyncio
import time
import base64
import json
import httpx
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

from fastapi import FastAPI, Depends, Query, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlmodel import Session, select, col
from sqlalchemy import update, func, or_, and_, case, cast, text, BigInteger
from pydantic import BaseModel, Field as PydField
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.core.database import init_db, get_session, get_script_session, engine as db_engine
from app.models import Article, Trend, Digest, SavedArticle, Feedback, IngestRun
from app.services import fetcher
from app.services.fetcher import ingest_intelligence
from app.services.analyzer import (
    analyze_articles,
    retry_failed_insights,
    generate_deep_brief,
    chat_about_article,
    generate_chat_suggestions,
    get_embed_model,
    generate_weekly_digest,
    probe_groq,
    get_last_ai_error,
)
from app.services.extractor import extract_article_content

scheduler = AsyncIOScheduler()

# Scheduler observability (updated by scheduled_ingest)
_scheduler_interval_hours = 4
_last_ingest_at_utc: str | None = None
_last_ingest_ok: bool | None = None
_last_ingest_detail: str = ""

# ---------------------------------------------------------------------------
# Rate limiting — keyed by authenticated user ID (falls back to IP)
# ---------------------------------------------------------------------------

def _rate_limit_key(request: Request) -> str:
    return request.headers.get("X-Axon-User-Id") or get_remote_address(request)

limiter = Limiter(key_func=_rate_limit_key)

# ---------------------------------------------------------------------------
# In-memory suggestions cache — avoids re-generating on every article open
# TTL: 6 hours per article. Bounded so a long-lived process can't grow it
# forever (one entry per article ever opened).
# ---------------------------------------------------------------------------

_suggestions_cache: dict[int, tuple[list[str], float]] = {}
_SUGGESTIONS_TTL = 6 * 3600  # seconds
_SUGGESTIONS_MAX = 512

def _get_cached_suggestions(article_id: int) -> list[str] | None:
    entry = _suggestions_cache.get(article_id)
    if entry and (time.time() - entry[1]) < _SUGGESTIONS_TTL:
        return entry[0]
    return None

def _set_cached_suggestions(article_id: int, suggestions: list[str]) -> None:
    if len(_suggestions_cache) >= _SUGGESTIONS_MAX:
        oldest = min(_suggestions_cache, key=lambda k: _suggestions_cache[k][1])
        del _suggestions_cache[oldest]
    _suggestions_cache[article_id] = (suggestions, time.time())


# ---------------------------------------------------------------------------
# Tiny TTL caches for hot read endpoints. These are polled by every client but
# their data only changes on ingest cadence (hours) or view cadence (seconds),
# so serving from memory keeps the DB out of the hot path. Safe because the
# deployment runs a single worker (see Dockerfile: APScheduler constraint).
# ---------------------------------------------------------------------------

class TTLCache:
    def __init__(self, ttl_seconds: float):
        self.ttl = ttl_seconds
        self._value = None
        self._at = 0.0

    def get(self):
        if self._value is not None and (time.time() - self._at) < self.ttl:
            return self._value
        return None

    def set(self, value) -> None:
        self._value = value
        self._at = time.time()

    def clear(self) -> None:
        self._value = None
        self._at = 0.0


_trending_cache = TTLCache(60)
_trends_cache = TTLCache(300)
_digest_cache = TTLCache(300)
_db_health_cache = TTLCache(30)
_pulse_cache = TTLCache(60)


def _feed_dump(articles) -> list[dict]:
    """Serialize articles for list payloads. Excludes full_content (up to 8KB
    per article) — the reader fetches it separately via /articles/{id}/content."""
    return [a.model_dump(exclude={"full_content"}) for a in articles]

INTERNAL_SECRET = os.getenv("AXON_INTERNAL_SECRET", "").strip()
# Keep Swagger/ReDoc private in production unless explicitly enabled.
EXPOSE_API_DOCS = os.getenv("EXPOSE_API_DOCS", "").strip().lower() in ("1", "true", "yes")
if not INTERNAL_SECRET:
    raise RuntimeError("Missing required env var: AXON_INTERNAL_SECRET")

# Frontend base URL used to fan Web Push notifications out after a productive ingest.
# Optional: when unset, push notifications are simply skipped (see _notify_new_signals).
FRONTEND_URL = os.getenv("AXON_FRONTEND_URL", "").strip()

# Admin dashboard allow-list. Comma-separated Better-Auth user IDs that may read
# /admin/stats. Fail closed: if unset, nobody is admin (the dashboard tells the
# user their own ID so they can add it here on both backend + frontend).
ADMIN_USER_IDS = {
    uid.strip() for uid in os.getenv("AXON_ADMIN_USER_IDS", "").split(",") if uid.strip()
}


def require_admin(request: Request) -> None:
    """Backstop auth for /admin/*. The internal-secret middleware already ran; this
    additionally checks the proxied user ID against AXON_ADMIN_USER_IDS so a normal
    logged-in user can't reach admin data through the shared /api/backend proxy."""
    if not ADMIN_USER_IDS:
        raise HTTPException(
            status_code=403,
            detail="Admin access not configured. Set AXON_ADMIN_USER_IDS on the backend.",
        )
    if request.headers.get("X-Axon-User-Id") not in ADMIN_USER_IDS:
        raise HTTPException(status_code=403, detail="Forbidden: not an admin user.")


# ---------------------------------------------------------------------------
# Backlog processing — analyze + retry as a background job.
#
# analyze_articles / retry_failed_insights sleep 12s between batches, so running
# them inside a request would take many minutes and time out the proxy (the
# "Retry insights failed: API 500" you'd otherwise see). The admin "Process
# backlog" button fires this and returns immediately; the dashboard polls
# _processing for live progress.
# ---------------------------------------------------------------------------

_processing: dict = {
    "running": False,
    "phase": None,        # "analyze" | "retry" | "done"
    "done": 0,
    "total": 0,
    "started_at": None,
    "finished_at": None,
    "result": None,
}


async def _run_backlog():
    global _processing
    _processing = {
        "running": True,
        "phase": "analyze",
        "done": 0,
        "total": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": None,
        "result": None,
    }

    def progress(done: int, total: int, phase: str) -> None:
        _processing["done"] = done
        _processing["total"] = total
        _processing["phase"] = phase

    session = get_script_session()
    try:
        analyzed = await asyncio.to_thread(analyze_articles, session, progress)
        retried = await asyncio.to_thread(retry_failed_insights, session, progress)
        _processing["result"] = f"analyzed {analyzed}, retried {retried}"
    except Exception as e:
        _processing["result"] = f"error: {str(e)[:300]}"
        print(f"AXON BACKLOG ERROR: {e}")
    finally:
        _processing["phase"] = "done"
        _processing["running"] = False
        _processing["finished_at"] = datetime.now(timezone.utc).isoformat()
        session.close()


# Cached Groq liveness — probe at most once per 5 min so the 30s stats poll never
# spends an LLM round-trip per refresh.
_groq_probe_cache: dict = {"at": 0.0, "value": None}


def _groq_status() -> dict:
    now = time.time()
    if _groq_probe_cache["value"] is None or now - _groq_probe_cache["at"] > 300:
        _groq_probe_cache["value"] = probe_groq()
        _groq_probe_cache["at"] = now
    return _groq_probe_cache["value"]

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]


def _record_ingest_run(trigger: str, ok: bool, new_articles: int, analyzed: int,
                       detail: str | None, started_at: datetime) -> None:
    """Persist one ingest run so the dashboard's history survives restarts."""
    try:
        report = fetcher.last_fetch_report or {}
        run = IngestRun(
            started_at=started_at,
            finished_at=datetime.now(timezone.utc),
            trigger=trigger,
            ok=ok,
            new_articles=new_articles,
            analyzed=analyzed,
            raw_found=int(report.get("raw") or 0),
            sources_json=json.dumps(report.get("sources") or {}),
            detail=(detail or "")[:500] or None,
        )
        s = get_script_session()
        try:
            s.add(run)
            s.commit()
        finally:
            s.close()
    except Exception as e:
        print(f"AXON: failed to record ingest run: {e}")


PUSH_MAX_PER_SWEEP = 2
PUSH_MAX_PER_DAY = 10
# A new story must score in the top 20% of the last 7 days to earn a push.
PUSH_SCORE_PERCENTILE = 0.8


def _pick_push_stories(session: Session, since_id: int, now: datetime | None = None) -> list[Article]:
    """The new stories worth a push: at most PUSH_MAX_PER_SWEEP, never past
    PUSH_MAX_PER_DAY per UTC day, and only ones scoring above the weekly bar."""
    now = now or datetime.now(timezone.utc)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    sent_today = session.exec(
        select(func.count()).select_from(Article).where(col(Article.notified_at) >= day_start)
    ).one() or 0
    budget = min(PUSH_MAX_PER_SWEEP, PUSH_MAX_PER_DAY - sent_today)
    if budget <= 0:
        return []
    week_scores = sorted(session.exec(
        select(Article.engagement_score).where(col(Article.published_date) >= now - timedelta(days=7))
    ).all())
    bar = week_scores[int(len(week_scores) * PUSH_SCORE_PERCENTILE)] if week_scores else 0.0
    return list(session.exec(
        select(Article)
        .where(col(Article.id) > since_id)
        .where(col(Article.notified_at).is_(None))
        .where(col(Article.engagement_score) >= bar)
        .order_by(col(Article.engagement_score).desc(), col(Article.id).desc())
        .limit(budget)
    ).all())


async def _notify_new_signals(session: Session, new_count: int, since_id: int = 0) -> None:
    """Push the strongest new stories, one notification each, via the frontend
    after a productive ingest. Best-effort: a missing AXON_FRONTEND_URL, a timeout,
    or any other error is swallowed so a push failure can never break or delay
    ingestion. The frontend endpoint owns the subscriber list + web-push (see
    fronted/src/routes/api/push/notify)."""
    if new_count <= 0:
        return
    if not FRONTEND_URL:
        print("AXON: push notify skipped — AXON_FRONTEND_URL is not set")
        return
    try:
        stories = _pick_push_stories(session, since_id)
        if not stories:
            print("AXON: push notify skipped — no story cleared the bar, or the daily cap is reached")
            return
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{FRONTEND_URL.rstrip('/')}/api/push/notify",
                headers={"X-Axon-Internal-Secret": INTERNAL_SECRET},
                json={
                    "count": new_count,
                    "stories": [
                        {"id": a.id, "title": a.title, "source": a.source, "likes": a.likes}
                        for a in stories
                    ],
                },
            )
        if resp.status_code >= 400:
            print(f"AXON: push notify failed: HTTP {resp.status_code} {resp.text[:200]}")
            return
        sent_at = datetime.now(timezone.utc)
        for a in stories:
            a.notified_at = sent_at
            session.add(a)
        session.commit()
        print(f"AXON: push notify ok ({resp.status_code}, {len(stories)} stories)")
    except Exception as e:
        print(f"AXON: push notify failed: {e}")


def _max_article_id(session: Session) -> int:
    return session.exec(select(func.max(Article.id))).one() or 0


async def scheduled_weekly_digest():
    """One digest a week, Sunday 06:00 UTC.

    Skips only if a digest was written in the last 12 hours, so each gunicorn
    worker's scheduler doesn't write its own copy. A manual digest earlier in
    the week must not cancel Sunday's.
    """
    session = get_script_session()
    try:
        latest = session.exec(select(Digest).order_by(col(Digest.created_at).desc())).first()
        if latest and latest.created_at:
            created = latest.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            age = datetime.now(timezone.utc) - created
            if age < timedelta(hours=12):
                print(f"AXON: weekly digest skipped — last one is {age.days}d {age.seconds // 3600}h old")
                return
        content = await asyncio.to_thread(generate_weekly_digest, session)
        if content:
            _digest_cache.clear()
            print(f"AXON: weekly digest written ({len(content)} chars)")
        else:
            print("AXON: weekly digest skipped — no articles")
    except Exception as e:
        print(f"AXON: weekly digest failed: {e}")
    finally:
        session.close()


async def scheduled_ingest():
    """Runs ingestion + analysis on a timer."""
    global _last_ingest_at_utc, _last_ingest_ok, _last_ingest_detail
    started = datetime.now(timezone.utc)
    new_count = 0
    analyzed = 0
    session = get_script_session()
    try:
        since_id = _max_article_id(session)
        new_count = await ingest_intelligence(session)
        if new_count > 0:
            # Notify as soon as stories land; analysis can take hours and only adds briefs.
            await _notify_new_signals(session, new_count, since_id)
            try:
                # analyze_articles is blocking (sync Groq calls + time.sleep between
                # batches). Run it off the event loop so the API stays responsive
                # while the scheduled analysis runs.
                analyzed = await asyncio.to_thread(analyze_articles, session)
            except Exception as ae:
                print(f"AXON SCHEDULER: analyze after ingest failed: {ae}")
                analyzed = 0
            _last_ingest_ok = True
            _last_ingest_detail = f"ingested {new_count} new, analyzed {analyzed} articles"
            print(f"AXON SCHEDULER: Ingested {new_count}, analyzed {analyzed}")
        else:
            _last_ingest_ok = True
            _last_ingest_detail = "no new signals (dedupe or empty run)"
            print("AXON SCHEDULER: No new signals")
    except Exception as e:
        _last_ingest_ok = False
        _last_ingest_detail = str(e)[:500]
        print(f"AXON SCHEDULER ERROR: {e}")
    finally:
        _last_ingest_at_utc = datetime.now(timezone.utc).isoformat()
        session.close()
        _record_ingest_run("scheduler", _last_ingest_ok or False, new_count, analyzed,
                           _last_ingest_detail, started)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler_interval_hours
    init_db()
    # Scheduled ingest only runs while this process is alive. Use a long-lived
    # host (container/VM), not a serverless cold-start model, or the interval
    # will not fire reliably. Override cadence with env INGEST_INTERVAL_HOURS.
    # Set DISABLE_SCHEDULER=1 if you trigger ingest only via Vercel Cron (see README).
    _scheduler_interval_hours = int(os.getenv("INGEST_INTERVAL_HOURS", "4"))
    disable_sched = os.getenv("DISABLE_SCHEDULER", "").lower() in ("1", "true", "yes")
    if not disable_sched:
        scheduler.add_job(
            scheduled_ingest,
            trigger=IntervalTrigger(hours=_scheduler_interval_hours),
            id="axon_ingest",
            replace_existing=True,
        )
        scheduler.add_job(
            scheduled_weekly_digest,
            trigger=CronTrigger(day_of_week="sun", hour=6, minute=0, timezone="UTC"),
            id="axon_weekly_digest",
            replace_existing=True,
            misfire_grace_time=6 * 3600,
        )
        scheduler.start()
        print(f"AXON: Scheduler started (ingest every {_scheduler_interval_hours}h, digest Sundays 06:00 UTC)")
    else:
        print("AXON: APScheduler disabled (DISABLE_SCHEDULER=1) — use external cron if needed")

    if os.getenv("INGEST_RUN_ON_STARTUP", "").lower() in ("1", "true", "yes"):
        asyncio.create_task(scheduled_ingest())
        print("AXON: INGEST_RUN_ON_STARTUP: queued initial ingest task")

    yield
    if scheduler.running:
        scheduler.shutdown()


app = FastAPI(title="Axon Intelligence Engine", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    lambda req, exc: JSONResponse(
        {"detail": "Rate limit exceeded. Please slow down."},
        status_code=429,
        headers={"Retry-After": "60"},
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Feed pages are highly compressible JSON (often 50-100KB raw); gzip cuts them
# ~5-10x, which matters most for the mobile PWA audience.
app.add_middleware(GZipMiddleware, minimum_size=1024)


@app.middleware("http")
async def require_internal_auth(request: Request, call_next):
    """When AXON_INTERNAL_SECRET is set, require SvelteKit proxy headers (see fronted /api/backend)."""
    path = request.url.path
    docs_paths = path in ("/docs", "/openapi.json", "/redoc") or path.startswith("/docs")
    if docs_paths:
        if EXPOSE_API_DOCS:
            return await call_next(request)
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    if not INTERNAL_SECRET:
        return await call_next(request)
    # Public health for uptime monitors (no internal secret).
    # Allow HEAD too — most monitors (Better Stack, etc.) probe with HEAD.
    if request.method in ("GET", "HEAD") and path in ("/", "/health"):
        return await call_next(request)
    if request.method == "OPTIONS":
        return await call_next(request)
    if request.headers.get("X-Axon-Internal-Secret") != INTERNAL_SECRET:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    if not request.headers.get("X-Axon-User-Id"):
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    return await call_next(request)


# ---------------------------------------------------------------------------
# Ingestion & Analysis (manual triggers still available)
# ---------------------------------------------------------------------------

@app.post("/ingest")
@limiter.limit("5/hour")
async def trigger_ingestion(request: Request, context_id: str | None = Query(default=None), force: bool = Query(default=False), session: Session = Depends(get_session)):
    global _last_ingest_at_utc

    # Global cooldown: skip if ingest happened within the interval (unless context-
    # specific, or force=true — the admin dashboard's "Run ingest now" sets force).
    if not force and not context_id and _last_ingest_at_utc:
        last_dt = datetime.fromisoformat(_last_ingest_at_utc)
        hours_since = (datetime.now(timezone.utc) - last_dt).total_seconds() / 3600
        if hours_since < _scheduler_interval_hours:
            return {
                "status": "skipped",
                "reason": f"Last ingest was {hours_since:.1f}h ago. Cooldown: {_scheduler_interval_hours}h",
                "new_articles": 0
            }
    
    started = datetime.now(timezone.utc)
    since_id = _max_article_id(session)
    count = await ingest_intelligence(session, context_id)
    _last_ingest_at_utc = datetime.now(timezone.utc).isoformat()
    _record_ingest_run("manual", True, count, 0, f"manual ingest ({context_id or 'ALL'})", started)
    await _notify_new_signals(session, count, since_id)
    return {"status": "success", "new_articles": count}


@app.post("/analyze")
async def trigger_analysis():
    """Non-blocking: launches the background analyze+retry job. (Was a sync def
    with 12s batch sleeps that could freeze the event loop for minutes.)"""
    if _processing["running"]:
        return {"status": "already_running"}
    asyncio.create_task(_run_backlog())
    return {"status": "started"}


@app.post("/retry-insights")
async def trigger_retry_insights():
    if _processing["running"]:
        return {"status": "already_running"}
    asyncio.create_task(_run_backlog())
    return {"status": "started"}


# ---------------------------------------------------------------------------
# Articles — cursor-based pagination
# ---------------------------------------------------------------------------

def _feed_sort_key():
    """day-bucket (UTC days since epoch) * 1000 + the article's ingest score in
    hundredths (0-999). A newer day always outranks an older one; within a day the
    best-scored stories lead. Deterministic and stable per row, so it's safe to
    keyset-paginate on."""
    raw = cast(func.floor(func.coalesce(Article.engagement_score, 0) * 100), BigInteger)
    score = case((raw > 999, 999), else_=raw)
    day_bucket = cast(func.floor(func.extract("epoch", Article.published_date) / 86400.0), BigInteger)
    return day_bucket * 1000 + score


def _highest_sort_key():
    """Stored score in hundred-thousandths. Highest is a 7-day reorder of the same
    number the day feed uses, so the key only has to stay stable for pagination."""
    return cast(func.floor(func.coalesce(Article.engagement_score, 0) * 100000), BigInteger)


def _encode_cursor(sort_key: int, article_id: int) -> str:
    """Opaque cursor carrying the keyset (feed_sort_key, id)."""
    raw = f"{int(sort_key)}|{article_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _decode_cursor(cursor: str) -> tuple[int, int]:
    raw = base64.urlsafe_b64decode(cursor.encode()).decode()
    key_str, id_str = raw.rsplit("|", 1)
    return int(key_str), int(id_str)


@app.get("/articles")
def read_articles(
    limit: int = Query(default=10, le=100),
    cursor: str | None = Query(default=None),
    category: str | None = Query(default=None),
    source: str | None = Query(default=None),
    order: str | None = Query(default=None),
    session: Session = Depends(get_session),
):
    # Default sort key = day-bucket * 1000 + ingest score, so the feed reads
    # "newest day first, best stories first within a day". `order=highest`
    # ignores the day and lists the strongest stored scores from the last 7
    # days. id is the unique tiebreaker. The key is deterministic, so cursoring
    # never skips or duplicates rows. The cursor carries (sort_key, id).
    #
    # Optional `category`/`source` filters scope the feed to a single tab. They're
    # plain WHERE clauses applied before the keyset predicate, so each tab is its
    # own properly-paginated feed (Load More returns the next page *of that tab*,
    # not the next page of the global feed).
    if order not in (None, "highest"):
        raise HTTPException(status_code=422, detail="order must be 'highest'")
    highest = order == "highest"
    sk = _highest_sort_key() if highest else _feed_sort_key()
    query = select(Article, sk.label("sk")).order_by(sk.desc(), col(Article.id).desc())
    if highest:
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        query = query.where(col(Article.published_date) >= cutoff)
    if category:
        query = query.where(Article.category == category)
    if source:
        query = query.where(Article.source == source)
    if cursor:
        try:
            c_key, c_id = _decode_cursor(cursor)
            query = query.where(
                or_(sk < c_key, and_(sk == c_key, col(Article.id) < c_id))
            )
        except Exception:
            pass  # malformed/legacy cursor -> serve from the top

    query = query.limit(limit)

    rows = session.exec(query).all()
    articles = [r[0] for r in rows]
    has_more = len(articles) == limit
    next_cursor = _encode_cursor(rows[-1][1], rows[-1][0].id) if (rows and has_more) else None

    return {
        "articles": _feed_dump(articles),
        "next_cursor": next_cursor,
        "has_more": has_more,
    }


@app.get("/articles/trending")
def get_trending_articles(
    session: Session = Depends(get_session),
):
    # Hot algorithmic sort: views / ((hours_since_published + 2)^1.8)
    # Since we might be using SQLite or Postgres and cross-compatibility is hard with math,
    # we'll fetch recent articles and compute the score, then sort and return.
    # Cached for 60s: every client polls this, but the ranking only moves as
    # fast as views accumulate.
    cached = _trending_cache.get()
    if cached is not None:
        return cached

    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    # Cap the scan so a growing corpus can't make this endpoint load unbounded
    # rows into memory; 2000 newest is far more than a week ever produces.
    query = (
        select(Article)
        .where(col(Article.published_date) >= cutoff)
        .order_by(col(Article.published_date).desc())
        .limit(2000)
    )
    recent_articles = session.exec(query).all()

    def calculate_hot_score(article: Article) -> float:
        views = article.views or 0
        likes = article.likes or 0
        base_score = views + (likes * 5)
        # Handle timezone naive vs aware
        pub_date = article.published_date
        if pub_date.tzinfo is None:
            pub_date = pub_date.replace(tzinfo=timezone.utc)
        hours_since = (datetime.now(timezone.utc) - pub_date).total_seconds() / 3600
        return base_score / ((hours_since + 2) ** 1.8)

    recent_articles.sort(key=calculate_hot_score, reverse=True)
    payload = {"articles": _feed_dump(recent_articles[:30])}
    _trending_cache.set(payload)
    return payload


@app.get("/saved")
def get_saved_articles(
    request: Request,
    session: Session = Depends(get_session),
):
    user_id = request.headers.get("X-Axon-User-Id")
    if not user_id:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    
    saved = session.exec(select(SavedArticle).where(SavedArticle.user_id == user_id)).all()
    article_ids = [s.article_id for s in saved]
    if not article_ids:
        return {"articles": []}
    
    articles = session.exec(select(Article).where(col(Article.id).in_(article_ids))).all()
    return {"articles": _feed_dump(articles)}


@app.post("/articles/{article_id}/save")
def toggle_save_article(
    article_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    user_id = request.headers.get("X-Axon-User-Id")
    if not user_id:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    
    existing = session.get(SavedArticle, {"user_id": user_id, "article_id": article_id})
    if existing:
        session.delete(existing)
        session.commit()
        return {"status": "removed"}
    else:
        new_save = SavedArticle(user_id=user_id, article_id=article_id) # type: ignore
        session.add(new_save)
        session.commit()
        return {"status": "saved"}


# ---------------------------------------------------------------------------
# Check for new articles (lightweight, no data transfer)
# ---------------------------------------------------------------------------

@app.get("/articles/count-since")
def count_since(
    since_id: int = Query(...),
    session: Session = Depends(get_session),
):
    count = session.exec(
        select(func.count()).select_from(Article).where(col(Article.id) > since_id)
    ).one()
    return {"new_count": count}


# Declared after /articles/trending and /articles/count-since: an int path
# parameter declared first would answer those paths with a 422.
@app.get("/articles/{article_id}")
def read_article(article_id: int, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return _feed_dump([article])[0]


# ---------------------------------------------------------------------------
# Article content extraction
# ---------------------------------------------------------------------------

@app.get("/articles/{article_id}/content")
@limiter.limit("60/minute")
async def get_article_content(request: Request, article_id: int, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.full_content:
        return {"content": article.full_content}

    content = await extract_article_content(article.url)
    if content:
        article.full_content = content
        session.add(article)
        session.commit()

    return {"content": content or article.content_snippet or ""}


# ---------------------------------------------------------------------------
# Semantic Search
# ---------------------------------------------------------------------------

@app.get("/search/semantic")
@limiter.limit("20/minute")
def search_semantic(request: Request, query: str = Query(..., min_length=1, max_length=200), session: Session = Depends(get_session)):
    model = get_embed_model()
    query_embed = list(model.embed([query]))[0].tolist()
    
    results = session.exec(
        select(Article)
        .where(Article.embedding != None) # type: ignore
        .order_by(Article.embedding.cosine_distance(query_embed))
        .limit(15)
    ).all()

    return {"articles": _feed_dump(results)}


# ---------------------------------------------------------------------------
# Briefs & Chat
# ---------------------------------------------------------------------------

@app.get("/brief/{article_id}")
@limiter.limit("10/minute")
def get_brief(request: Request, article_id: int, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    brief = generate_deep_brief(article.title, article.full_content or article.content_snippet or "")
    return {"title": article.title, "brief": brief}


class ChatRequest(BaseModel):
    # Bounded so a single request can't blow up Groq token cost.
    question: str = PydField(..., min_length=1, max_length=1000)


class FeedbackRequest(BaseModel):
    rating: int
    comment: str | None = None


@app.get("/articles/{article_id}/suggestions")
@limiter.limit("30/minute")
def article_chat_suggestions(request: Request, article_id: int, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    # Serve from cache if fresh — avoids expensive LLM call on every article open
    cached = _get_cached_suggestions(article_id)
    if cached:
        return {"suggestions": cached, "cached": True}
    suggestions = generate_chat_suggestions(
        title=article.title,
        content_snippet=article.content_snippet or "",
        insight=article.insight or "",
        category=article.category,
        source=article.source,
    )
    _set_cached_suggestions(article_id, suggestions)
    return {"suggestions": suggestions, "cached": False}


@app.post("/articles/{article_id}/chat")
@limiter.limit("20/minute")
async def article_chat(request: Request, article_id: int, req: ChatRequest, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    # Fetch the linked page the first time someone asks, then keep it.
    content = article.full_content
    if not content:
        content = await extract_article_content(article.url)
        if content:
            article.full_content = content
            session.add(article)
            session.commit()
    text = (content or article.content_snippet or "").strip()
    if not text:
        return {"answer": "The source text isn't available, so I can't answer from it."}
    answer = chat_about_article(
        title=article.title,
        content=text,
        insight="",
        question=req.question,
    )
    return {"answer": answer}


# ---------------------------------------------------------------------------
# Engagement
# ---------------------------------------------------------------------------

@app.post("/articles/{article_id}/view")
def track_view(article_id: int, session: Session = Depends(get_session)):
    stmt = (
        update(Article)
        .where(Article.id == article_id)
        .values(views=Article.views + 1, last_viewed=datetime.now(timezone.utc))
    )
    session.execute(stmt)
    session.commit()
    return {"status": "success"}


# ---------------------------------------------------------------------------
# Weekly Digest
# ---------------------------------------------------------------------------

@app.get("/digests/latest")
def get_latest_digest(session: Session = Depends(get_session)):
    cached = _digest_cache.get()
    if cached is not None:
        return cached
    digest = session.exec(select(Digest).order_by(col(Digest.created_at).desc()).limit(1)).first()
    if not digest:
        return {"content": "No weekly digest available yet."}
    payload = {"content": digest.content, "created_at": digest.created_at}
    _digest_cache.set(payload)
    return payload

@app.post("/digests/generate")
@limiter.limit("3/hour")
def trigger_digest(request: Request, session: Session = Depends(get_session)):
    require_admin(request)
    content = generate_weekly_digest(session)
    if not content:
        return JSONResponse(
            {"status": "error", "detail": "No articles available to generate a weekly digest yet."},
            status_code=503,
        )
    _digest_cache.clear()
    return {"status": "success", "digest": content}


# ---------------------------------------------------------------------------
# Trends
# ---------------------------------------------------------------------------

@app.get("/trends")
def read_trends(session: Session = Depends(get_session)):
    from datetime import date, timedelta

    # Trends are recomputed at ingest time (every few hours) — 5 min of cache
    # costs nothing in freshness and absorbs every client's poll.
    cached = _trends_cache.get()
    if cached is not None:
        return cached

    # Get the most recent date we have trend data for (may not be today)
    latest_date = session.exec(
        select(Trend.trend_date).order_by(col(Trend.trend_date).desc()).limit(1)
    ).first()

    if not latest_date:
        return []

    today_trends = session.exec(
        select(Trend).where(Trend.trend_date == latest_date).order_by(col(Trend.count).desc()).limit(12)
    ).all()

    # Load yesterday's counts for velocity comparison
    prev_date = latest_date - timedelta(days=1)
    prev_counts: dict[str, int] = {
        t.keyword: t.count
        for t in session.exec(select(Trend).where(Trend.trend_date == prev_date)).all()
    }

    result = []
    for t in today_trends:
        prev = prev_counts.get(t.keyword, 0)
        if prev == 0:
            velocity = "New"
            is_new = True
        elif t.count >= prev * 2:
            velocity = "Surging"
            is_new = False
        elif t.count > prev:
            velocity = "Rising"
            is_new = False
        else:
            velocity = "Steady"
            is_new = False

        result.append({
            "keyword": t.keyword,
            "count": t.count,
            "velocity": velocity,
            "is_new": is_new,
        })

    _trends_cache.set(result)
    return result

# ---------------------------------------------------------------------------
# RSS
# ---------------------------------------------------------------------------

@app.get("/rss")
def get_rss_feed(session: Session = Depends(get_session)):
    articles = session.exec(select(Article).order_by(col(Article.published_date).desc()).limit(20)).all()
    
    xml = ['<?xml version="1.0" encoding="UTF-8" ?>', '<rss version="2.0">', '<channel>']
    xml.append('<title>Axon Intelligence Feed</title>')
    xml.append('<link>https://axon.example.com</link>')
    xml.append('<description>Top AI and Tech signals</description>')
    
    for a in articles:
        xml.append('<item>')
        xml.append(f'<title><![CDATA[{a.title}]]></title>')
        xml.append(f'<link>{a.url}</link>')
        xml.append(f'<description><![CDATA[{a.insight or a.content_snippet or ""}]]></description>')
        xml.append('</item>')
        
    xml.append('</channel></rss>')
    
    return Response(content="\n".join(xml), media_type="application/rss+xml")
    
@app.post("/feedback")
@limiter.limit("5/hour")
def submit_feedback(request: Request, payload: FeedbackRequest, session: Session = Depends(get_session)):
    user_id = request.headers.get("X-Axon-User-Id")
    if not user_id:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    if not (1 <= payload.rating <= 5):
        raise HTTPException(status_code=422, detail="rating must be between 1 and 5")

    entry = Feedback(
        user_id=user_id,
        rating=payload.rating,
        comment=payload.comment,
        created_at=datetime.now(timezone.utc),
    )
    session.add(entry)
    session.commit()
    return {"status": "success"}

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {
        "status": "Axon is online",
        "scheduler_running": scheduler.running,
        "details": "/health",
    }


def _scheduler_snapshot() -> dict:
    job = scheduler.get_job("axon_ingest") if scheduler.running else None
    next_run = job.next_run_time.isoformat() if (job and job.next_run_time) else None
    return {
        "ap_scheduler_running": scheduler.running,
        "interval_hours": _scheduler_interval_hours,
        "job_registered": job is not None,
        "next_run_at_utc": next_run,
    }


def _last_ingest_snapshot() -> dict:
    relative = None
    if _last_ingest_at_utc:
        try:
            delta = datetime.now(timezone.utc) - datetime.fromisoformat(_last_ingest_at_utc)
            secs = delta.total_seconds()
            if secs < 60:
                relative = "just now"
            elif secs < 3600:
                relative = f"{int(secs // 60)}m ago"
            else:
                relative = f"{int(secs // 3600)}h ago"
        except Exception:
            pass
    return {
        "at_utc": _last_ingest_at_utc,
        "ok": _last_ingest_ok,
        "detail": _last_ingest_detail or None,
        "relative": relative,
    }


def _db_status() -> dict:
    """Cheap DB liveness (SELECT 1), cached 30s so keep-alive pings don't hold
    a pool connection per probe and a dead DB doesn't get hammered."""
    cached = _db_health_cache.get()
    if cached is not None:
        return cached
    try:
        with db_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        value = {"ok": True, "error": None}
    except Exception as e:
        value = {"ok": False, "error": str(e)[:200]}
    _db_health_cache.set(value)
    return value


@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    """Public JSON for uptime checks and debugging ingest timing (no auth).

    Accepts HEAD as well as GET — uptime monitors (Better Stack, etc.) probe
    with HEAD, and a GET-only route would answer them with 405.
    """
    db = _db_status()
    return {
        "status": "ok" if db["ok"] else "degraded",
        "db": db,
        "service": "axon-api",
        "scheduler": _scheduler_snapshot(),
        "last_scheduled_ingest": _last_ingest_snapshot(),
        "hints": {
            "always_on": "APScheduler only fires while this process stays running.",
            "env_INGEST_INTERVAL_HOURS": _scheduler_interval_hours,
            "vercel_cron": "Optional: Vercel Cron can POST via frontend /api/cron/ingest — see project README.",
        },
    }


def _as_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


@app.get("/pulse")
def pulse(session: Session = Depends(get_session)):
    """What the filter did recently: items scanned vs. kept per sweep.

    Feeds the landing page readout and the app's sweep panel. Aggregates only —
    no per-source breakdown, prompts, or rules leave this endpoint.
    """
    cached = _pulse_cache.get()
    if cached is not None:
        return cached

    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(hours=24)

    last = session.exec(
        select(IngestRun)
        .where(IngestRun.ok == True)  # noqa: E712
        .order_by(col(IngestRun.started_at).desc())
        .limit(1)
    ).first()

    scanned_24h, kept_24h, runs_24h = session.exec(
        select(
            func.coalesce(func.sum(IngestRun.raw_found), 0),
            func.coalesce(func.sum(IngestRun.new_articles), 0),
            func.count(),
        ).where(IngestRun.ok == True, IngestRun.started_at >= day_ago)  # noqa: E712
    ).one()

    sources = session.exec(select(func.count(func.distinct(Article.source)))).one()
    kept_total = session.exec(select(func.count()).select_from(Article)).one()
    sweeps_total, scanned_total, first_at = session.exec(
        select(
            func.count(),
            func.coalesce(func.sum(IngestRun.raw_found), 0),
            func.min(IngestRun.started_at),
        ).where(IngestRun.ok == True)  # noqa: E712
    ).one()

    # The configured interval can differ from what actually runs (env drift,
    # host restarts), so report the cadence observed between recent sweeps.
    recent_starts = [
        _as_utc(t)
        for t in session.exec(
            select(IngestRun.started_at)
            .where(IngestRun.ok == True)  # noqa: E712
            .order_by(col(IngestRun.started_at).desc())
            .limit(7)
        ).all()
    ]
    gaps = sorted(
        (a - b).total_seconds() / 3600 for a, b in zip(recent_starts, recent_starts[1:])
    )
    interval = round(gaps[len(gaps) // 2]) if gaps else _scheduler_interval_hours
    interval = interval or _scheduler_interval_hours

    last_at = _as_utc(last.finished_at or last.started_at) if last else None
    next_at = _scheduler_snapshot()["next_run_at_utc"]
    if not next_at and last:
        next_at = (_as_utc(last.started_at) + timedelta(hours=interval)).isoformat()

    value = {
        "last_sweep_at": last_at.isoformat() if last_at else None,
        "last_scanned": last.raw_found if last else 0,
        "last_kept": last.new_articles if last else 0,
        "scanned_24h": int(scanned_24h or 0),
        "kept_24h": int(kept_24h or 0),
        "sweeps_24h": int(runs_24h or 0),
        "sources": int(sources or 0),
        "interval_hours": interval,
        "next_sweep_at": next_at,
        "kept_total": int(kept_total or 0),
        "sweeps_total": int(sweeps_total or 0),
        "scanned_total": int(scanned_total or 0),
        "running_since": _as_utc(first_at).isoformat() if first_at else None,
        "engine": "full"
        if {"axon_private_fetcher", "axon_private_analyzer"} <= sys.modules.keys()
        else "community",
    }
    _pulse_cache.set(value)
    return value


# ---------------------------------------------------------------------------
# Admin dashboard — aggregate health for ingestion / pipeline / engagement.
# Internal-secret middleware + require_admin (AXON_ADMIN_USER_IDS) gate this.
# ---------------------------------------------------------------------------

@app.get("/admin/stats")
def admin_stats(request: Request, session: Session = Depends(get_session)):
    require_admin(request)

    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(hours=24)
    week_ago = now - timedelta(days=7)
    fortnight_ago = now - timedelta(days=14)

    # insight is "missing" when null or empty — flags articles the AI step hasn't
    # (successfully) processed yet.
    missing_insight_pred = or_(col(Article.insight) == None, col(Article.insight) == "")  # noqa: E711

    total_articles = session.exec(select(func.count()).select_from(Article)).one()
    processed = session.exec(
        select(func.count()).select_from(Article).where(Article.is_processed == True)  # noqa: E712
    ).one()
    missing_insight = session.exec(
        select(func.count()).select_from(Article).where(missing_insight_pred)
    ).one()

    # Per-source health: volume + how stale the newest item is. A source whose
    # latest item is many hours/days old is probably failing to fetch silently.
    source_rows = session.exec(
        select(
            Article.source,
            func.count().label("total"),
            func.max(Article.published_date).label("latest"),
            func.sum(case((col(Article.published_date) >= day_ago, 1), else_=0)).label("d1"),
            func.sum(case((col(Article.published_date) >= week_ago, 1), else_=0)).label("d7"),
            func.sum(case((missing_insight_pred, 1), else_=0)).label("missing"),
        ).group_by(Article.source)
    ).all()

    sources = []
    for source, total, latest, d1, d7, missing in source_rows:
        latest_iso = None
        hours_since = None
        if latest is not None:
            if latest.tzinfo is None:
                latest = latest.replace(tzinfo=timezone.utc)
            latest_iso = latest.isoformat()
            hours_since = round((now - latest).total_seconds() / 3600, 1)
        sources.append({
            "source": source,
            "total": int(total or 0),
            "last_24h": int(d1 or 0),
            "last_7d": int(d7 or 0),
            "missing_insight": int(missing or 0),
            "latest_published": latest_iso,
            "hours_since_latest": hours_since,
        })
    # Stalest first so problems surface at the top of the table.
    sources.sort(key=lambda s: s["hours_since_latest"] if s["hours_since_latest"] is not None else 1e9, reverse=True)

    # Articles per day (last 14d) for a volume sparkline.
    day_col = func.date(Article.published_date)
    vol_rows = session.exec(
        select(day_col.label("day"), func.count().label("count"))
        .where(col(Article.published_date) >= fortnight_ago)
        .group_by(day_col)
        .order_by(day_col)
    ).all()
    daily_volume = [{"day": str(day), "count": int(count)} for day, count in vol_rows]

    total_views = session.exec(select(func.coalesce(func.sum(Article.views), 0))).one()
    # NOTE: Article.likes is the source's own popularity score (HN points, GitHub
    # stars), NOT a user "like" — summing it is only meaningful as a corpus signal.
    source_score_sum = session.exec(select(func.coalesce(func.sum(Article.likes), 0))).one()
    saved_count = session.exec(select(func.count()).select_from(SavedArticle)).one()
    feedback_count = session.exec(select(func.count()).select_from(Feedback)).one()
    avg_rating = session.exec(select(func.avg(Feedback.rating))).one()
    recent_feedback = session.exec(
        select(Feedback).order_by(col(Feedback.created_at).desc()).limit(8)
    ).all()
    recent_runs = session.exec(
        select(IngestRun).order_by(col(IngestRun.started_at).desc()).limit(20)
    ).all()

    return {
        "generated_at": now.isoformat(),
        "scheduler": _scheduler_snapshot(),
        "last_scheduled_ingest": _last_ingest_snapshot(),
        "ai": _groq_status(),
        "ai_last_error": get_last_ai_error(),
        "processing": _processing,
        "fetch_report": fetcher.last_fetch_report,
        "recent_runs": [
            {
                "id": r.id,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "finished_at": r.finished_at.isoformat() if r.finished_at else None,
                "trigger": r.trigger,
                "ok": r.ok,
                "new_articles": r.new_articles,
                "analyzed": r.analyzed,
                "raw_found": r.raw_found,
                "detail": r.detail,
            }
            for r in recent_runs
        ],
        "totals": {
            "articles": int(total_articles or 0),
            "processed": int(processed or 0),
            "unprocessed": int((total_articles or 0) - (processed or 0)),
            "missing_insight": int(missing_insight or 0),
            "trends": int(session.exec(select(func.count()).select_from(Trend)).one() or 0),
            "digests": int(session.exec(select(func.count()).select_from(Digest)).one() or 0),
            "feedback": int(feedback_count or 0),
            "saved": int(saved_count or 0),
        },
        "sources": sources,
        "daily_volume": daily_volume,
        "engagement": {
            "total_views": int(total_views or 0),
            "total_saves": int(saved_count or 0),
            "source_score_sum": int(source_score_sum or 0),
            "feedback_count": int(feedback_count or 0),
            "avg_feedback_rating": round(float(avg_rating), 2) if avg_rating is not None else None,
            "recent_feedback": [
                {
                    "user": (f.user_id[:8] + "…") if f.user_id and len(f.user_id) > 8 else f.user_id,
                    "rating": f.rating,
                    "comment": f.comment,
                    "created_at": f.created_at.isoformat() if f.created_at else None,
                }
                for f in recent_feedback
            ],
        },
    }


@app.post("/admin/process")
async def admin_process_backlog(request: Request):
    """Kick off background analyze + retry-insights. Returns immediately; the
    dashboard watches `processing` in /admin/stats for progress."""
    require_admin(request)
    if _processing["running"]:
        return {"status": "already_running", "processing": _processing}
    asyncio.create_task(_run_backlog())
    return {"status": "started"}
