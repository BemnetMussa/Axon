import os
import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

from fastapi import FastAPI, Depends, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlmodel import Session, select, col
from sqlalchemy import update, func
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.database import init_db, get_session, get_script_session
from app.models import Article, Trend, Digest, SavedArticle
from app.services.fetcher import ingest_intelligence
from app.services.analyzer import (
    analyze_articles,
    retry_failed_insights,
    generate_deep_brief,
    chat_about_article,
    generate_chat_suggestions,
    get_embed_model,
    generate_weekly_digest,
)
from app.services.extractor import extract_article_content

scheduler = AsyncIOScheduler()

# ---------------------------------------------------------------------------
# Rate limiting — keyed by authenticated user ID (falls back to IP)
# ---------------------------------------------------------------------------

def _rate_limit_key(request: Request) -> str:
    return request.headers.get("X-Axon-User-Id") or get_remote_address(request)

limiter = Limiter(key_func=_rate_limit_key)

# ---------------------------------------------------------------------------
# In-memory suggestions cache — avoids re-generating on every article open
# TTL: 6 hours per article
# ---------------------------------------------------------------------------

_suggestions_cache: dict[int, tuple[list[str], float]] = {}
_SUGGESTIONS_TTL = 6 * 3600  # seconds

def _get_cached_suggestions(article_id: int) -> list[str] | None:
    entry = _suggestions_cache.get(article_id)
    if entry and (time.time() - entry[1]) < _SUGGESTIONS_TTL:
        return entry[0]
    return None

def _set_cached_suggestions(article_id: int, suggestions: list[str]) -> None:
    _suggestions_cache[article_id] = (suggestions, time.time())

INTERNAL_SECRET = os.getenv("AXON_INTERNAL_SECRET", "").strip()
if not INTERNAL_SECRET:
    raise RuntimeError("Missing required env var: AXON_INTERNAL_SECRET")

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]


async def scheduled_ingest():
    """Runs ingestion + analysis on a timer."""
    session = get_script_session()
    try:
        count = await ingest_intelligence(session)
        if count > 0:
            analyzed = analyze_articles(session)
            print(f"AXON SCHEDULER: Ingested {count}, analyzed {analyzed}")
        else:
            print("AXON SCHEDULER: No new signals")
    except Exception as e:
        print(f"AXON SCHEDULER ERROR: {e}")
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Scheduled ingest only runs while this process is alive. Use a long-lived
    # host (container/VM), not a serverless cold-start model, or the interval
    # will not fire reliably. Override cadence with env INGEST_INTERVAL_HOURS.
    interval_hours = int(os.getenv("INGEST_INTERVAL_HOURS", "4"))
    scheduler.add_job(
        scheduled_ingest,
        trigger=IntervalTrigger(hours=interval_hours),
        id="axon_ingest",
        replace_existing=True,
    )
    scheduler.start()
    print(f"AXON: Scheduler started (every {interval_hours}h)")
    yield
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


@app.middleware("http")
async def require_internal_auth(request: Request, call_next):
    """When AXON_INTERNAL_SECRET is set, require SvelteKit proxy headers (see fronted /api/backend)."""
    if not INTERNAL_SECRET:
        return await call_next(request)
    path = request.url.path
    if path in ("/docs", "/openapi.json", "/redoc") or path.startswith("/docs"):
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
async def trigger_ingestion(request: Request, context_id: str | None = Query(default=None), session: Session = Depends(get_session)):
    count = await ingest_intelligence(session, context_id)
    return {"status": "success", "new_articles": count}


@app.post("/analyze")
def trigger_analysis(session: Session = Depends(get_session)):
    try:
        count = analyze_articles(session)
        return {"status": "success", "processed": count}
    except Exception as exc:
        print(f"[analyze] failed: {exc}")
        return {"status": "partial", "processed": 0}


@app.post("/retry-insights")
def trigger_retry_insights(session: Session = Depends(get_session)):
    count = retry_failed_insights(session)
    return {"status": "success", "retried": count}


# ---------------------------------------------------------------------------
# Articles — cursor-based pagination
# ---------------------------------------------------------------------------

@app.get("/articles")
def read_articles(
    limit: int = Query(default=10, le=100),
    cursor: int | None = Query(default=None),
    session: Session = Depends(get_session),
):
    query = select(Article).order_by(col(Article.published_date).desc())
    if cursor is not None:
        query = query.where(col(Article.id) < cursor)
    query = query.limit(limit)

    articles = session.exec(query).all()
    next_cursor = articles[-1].id if articles else None

    return {
        "articles": articles,
        "next_cursor": next_cursor,
        "has_more": len(articles) == limit,
    }


@app.get("/articles/trending")
def get_trending_articles(
    session: Session = Depends(get_session),
):
    # Hot algorithmic sort: views / ((hours_since_published + 2)^1.8)
    # Since we might be using SQLite or Postgres and cross-compatibility is hard with math,
    # we'll fetch recent articles and compute the score, then sort and return.
    cutoff = datetime.utcnow() - timedelta(days=7)
    query = select(Article).where(col(Article.published_date) >= cutoff)
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
    return {"articles": recent_articles[:30]}


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
    return {"articles": articles}


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


# ---------------------------------------------------------------------------
# Article content extraction
# ---------------------------------------------------------------------------

@app.get("/articles/{article_id}/content")
async def get_article_content(article_id: int, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        return {"error": "Not found"}

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
def search_semantic(query: str, session: Session = Depends(get_session)):
    model = get_embed_model()
    query_embed = list(model.embed([query]))[0].tolist()
    
    results = session.exec(
        select(Article)
        .where(Article.embedding != None) # type: ignore
        .order_by(Article.embedding.cosine_distance(query_embed))
        .limit(15)
    ).all()
    
    return {"articles": results}


# ---------------------------------------------------------------------------
# Briefs & Chat
# ---------------------------------------------------------------------------

@app.get("/brief/{article_id}")
def get_brief(article_id: int, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        return {"error": "Not found"}
    brief = generate_deep_brief(article.title, article.content_snippet or "")
    return {"title": article.title, "brief": brief}


class ChatRequest(BaseModel):
    question: str


@app.get("/articles/{article_id}/suggestions")
@limiter.limit("30/minute")
def article_chat_suggestions(request: Request, article_id: int, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        return {"error": "Not found", "suggestions": []}
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
def article_chat(request: Request, article_id: int, req: ChatRequest, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        return {"error": "Not found"}
    content = article.full_content or article.content_snippet or ""
    answer = chat_about_article(
        title=article.title,
        content=content,
        insight=article.insight or "",
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
        .values(views=Article.views + 1, last_viewed=datetime.utcnow())
    )
    session.execute(stmt)
    session.commit()
    return {"status": "success"}


# ---------------------------------------------------------------------------
# Weekly Digest
# ---------------------------------------------------------------------------

@app.get("/digests/latest")
def get_latest_digest(session: Session = Depends(get_session)):
    digest = session.exec(select(Digest).order_by(col(Digest.created_at).desc()).limit(1)).first()
    if not digest:
        return {"content": "No weekly digest available yet."}
    return {"content": digest.content, "created_at": digest.created_at}

@app.post("/digests/generate")
@limiter.limit("3/hour")
def trigger_digest(request: Request, session: Session = Depends(get_session)):
    content = generate_weekly_digest(session)
    if not content:
        return JSONResponse(
            {"status": "error", "detail": "No articles available to generate a weekly digest yet."},
            status_code=503,
        )
    return {"status": "success", "digest": content}


# ---------------------------------------------------------------------------
# Trends
# ---------------------------------------------------------------------------

@app.get("/trends")
def read_trends(session: Session = Depends(get_session)):
    from datetime import date, timedelta

    today = date.today()
    yesterday = today - timedelta(days=1)

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

@app.get("/")
def health():
    return {"status": "Axon is online", "scheduler": scheduler.running}
