import os
import httpx
import asyncio
import bisect
import feedparser
import math
import re
import html
from collections import Counter
from datetime import datetime, timedelta, timezone
from time import mktime
from sqlmodel import Session, select, col
from app.models import Article
from app.services.extractor import extract_article_content
from app.services.analyzer import classify_article
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# "bearer" for fine-grained PATs, "token" for classic PATs (default)
GITHUB_AUTH_STYLE = (os.getenv("GITHUB_AUTH_STYLE") or "token").strip().lower()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

DOMAIN_BLACKLIST = {
    "medium.com", "dev.to", "facebook.com", "linkedin.com",
    "designgurus.io", "geeksforgeeks.org", "youtube.com",
}

TITLE_FLUFF = {
    "career", "interview", "hired", "salary", "beginner",
    "roadmap", "job", "tutorial", "resume", "leetcode",
}

# Substrings that mark a GitHub repo as an evergreen "list/learning" project
# (curated link dumps, study guides) rather than a real tool worth surfacing.
# Checked against owner/repo only, so it won't touch other sources' titles.
GITHUB_NAME_FLUFF = {
    "awesome", "cheatsheet", "cheat-sheet", "free-programming",
    "programming-books", "-books", "coding-interview", "system-design",
    "build-your-own", "100-days", "30-days", "must-read", "curated",
    "the-book-of", "every-programmer",
}

MAX_PER_SOURCE = 5
MAX_TOTAL_PER_RUN = 20
# Only ingest genuinely recent items — a "what's happening now" feed should never
# surface months-old posts (stale RSS, resurfaced old HN threads, etc.).
FRESHNESS_DAYS = 30

# How many selected articles to hydrate with full body text per run, and how
# many of those fetches to run concurrently. Extraction skips aggregator
# domains (GitHub/HN/ArXiv/etc.) internally — for those the snippet IS the content.
FULL_CONTENT_CONCURRENCY = 8

# Per-source trust weights for ranking. Higher = inherently higher-signal, which
# matters most for RSS sources that carry no engagement number (likes == 0).
SOURCE_WEIGHTS = {
    "openai": 1.6, "anthropic": 1.6, "deepmind": 1.5, "googleai": 1.4, "huggingface": 1.4,
    "googleresearch": 1.3, "nvidia": 1.2, "together": 1.1,
    "karpathy": 1.5, "simonw": 1.4, "lilianweng": 1.4, "bair": 1.3,
    "altman": 1.3, "fast.ai": 1.2,
    "hackernews": 1.3, "github": 1.3, "arxiv": 1.2, "lobsters": 1.2,
    "techcrunch": 0.9, "theverge": 0.9, "arstechnica": 0.9, "producthunt": 1.0,
}
# Recency half-life-ish scale in hours (exp decay): ~3 days.
RECENCY_SCALE_HOURS = 72.0

# Telemetry from the most recent ingest run, surfaced on the admin dashboard so a
# source that returns nothing (rate-limited, moved feed) is visible immediately —
# the truth about "is this source being fetched", independent of publish dates.
# Mutated in place by ingest_intelligence; read by the API's /admin/stats.
last_fetch_report: dict = {"at": None, "raw": 0, "ingested": 0, "sources": {}}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _check_feed(name: str, entries: list) -> list:
    """Log a warning when a curated feed returns nothing, so dead feeds stop
    failing silently (every hunt_* swallows exceptions otherwise)."""
    if not entries:
        print(f"AXON WARNING: feed '{name}' returned 0 entries (moved/dead URL?)")
    return entries


def _parse_sitemap_date(s: str) -> datetime:
    """Parse a sitemap <lastmod> value (date or full ISO) into tz-aware UTC."""
    try:
        dt = datetime.fromisoformat(s.strip().replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return _now()


def _parse_feed_date(entry) -> datetime:
    """Extract publication date from a feedparser entry."""
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
            except Exception:
                pass
    return _now()


def is_gold(
    url: str,
    title: str,
    engagement: int = 0,
    source: str = "",
    fluff_text: str | None = None,
) -> bool:
    """fluff_text: if set, TITLE_FLUFF is checked against this only (e.g. GitHub owner/repo, not description).

    Junk filters (blacklist + fluff words) always run first — a high engagement
    count no longer buys a junk item a free pass. That bypass is exactly why
    all-time-famous repos (developer-roadmap, awesome-*) used to sail through.
    Traction is already enforced upstream by each hunter's query (HN front page,
    GitHub star floors, Lobsters hottest), and final ordering is handled by
    engagement_score, so anything clearing the junk filters is kept.
    """
    try:
        domain = url.split("/")[2].replace("www.", "")
        if any(bad in domain for bad in DOMAIN_BLACKLIST):
            return False
        check = (fluff_text if fluff_text is not None else title).lower()
        if any(w in check for w in TITLE_FLUFF):
            return False
        return True
    except Exception:
        return False


def _github_api_headers() -> dict[str, str]:
    """GitHub REST API requires User-Agent; merge with optional auth."""
    h = dict(HEADERS)
    if not GITHUB_TOKEN:
        return h
    if GITHUB_AUTH_STYLE == "bearer":
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    else:
        h["Authorization"] = f"token {GITHUB_TOKEN}"
    return h


# ---------------------------------------------------------------------------
# HACKER NEWS — top stories (what people are actually talking about)
# ---------------------------------------------------------------------------

async def hunt_hn_top(client: httpx.AsyncClient):
    """Fetch the current HN front-page stories with their point counts."""
    try:
        res = await client.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10.0
        )
        story_ids = res.json()[:20]

        async def fetch_story(sid: int):
            try:
                r = await client.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    timeout=8.0,
                )
                item = r.json()
                if not item or item.get("type") != "story":
                    return None
                url = item.get("url") or f"https://news.ycombinator.com/item?id={sid}"
                pub = datetime.fromtimestamp(item.get("time", 0), tz=timezone.utc) if item.get("time") else _now()
                return {
                    "title": item.get("title", ""),
                    "url": url,
                    "snippet": item.get("text", "")[:400] or item.get("title", ""),
                    "source": "HackerNews",
                    "category": "General",
                    "likes": item.get("score", 0),
                    "published": pub,
                }
            except Exception:
                return None

        stories = await asyncio.gather(*[fetch_story(sid) for sid in story_ids])
        return [s for s in stories if s and s["title"]]
    except Exception:
        return []


async def hunt_hn_discussions(client: httpx.AsyncClient):
    """Ask HN / Show HN — community discussions and launches."""
    # search_by_date (not relevance) so we get *current* threads — the relevance
    # endpoint was surfacing ancient high-comment Ask HN posts (back to 2012).
    url = "https://hn.algolia.com/api/v1/search_by_date?tags=(ask_hn,show_hn)&numericFilters=num_comments>2&hitsPerPage=15"
    try:
        res = await client.get(url, timeout=10.0)
        hits = res.json().get("hits", [])
        results = []
        for h in hits:
            pub = _now()
            if h.get("created_at"):
                try:
                    pub = datetime.fromisoformat(h["created_at"].replace("Z", "+00:00"))
                except Exception:
                    pass
            results.append({
                "title": h["title"],
                "url": f"https://news.ycombinator.com/item?id={h['objectID']}",
                "snippet": (h.get("story_text") or "")[:300] or h["title"],
                "source": "HackerNews",
                "category": "Discovery" if "show hn" in h["title"].lower() else "Concerns",
                "likes": h.get("points", 0),
                "published": pub,
            })
        return results
    except Exception:
        return []


# ---------------------------------------------------------------------------
# GITHUB — actually trending repos
# ---------------------------------------------------------------------------

async def hunt_github_trending(client: httpx.AsyncClient):
    """Multiple GitHub search strategies to surface genuinely trending repos."""
    gh_headers = _github_api_headers()
    signals: list[dict] = []

    async def search_github(query: str, label: str):
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=10"
        try:
            res = await client.get(url, headers=gh_headers, timeout=15.0)
            if res.status_code == 401 and "Authorization" in gh_headers:
                # An expired GITHUB_TOKEN silently killed this source for months;
                # anonymous search (10 req/min) easily covers a sweep's queries.
                print("AXON GitHub: token rejected (401), retrying without auth. Rotate GITHUB_TOKEN.")
                gh_headers.pop("Authorization", None)
                res = await client.get(url, headers=gh_headers, timeout=15.0)
            if res.status_code != 200:
                body = (res.text or "")[:400]
                print(f"AXON GitHub search HTTP {res.status_code} for q={query[:80]}... body={body}")
                return []
            items = res.json().get("items", [])
            results = []
            for i in items:
                if not (i.get("description") or "").strip():
                    continue
                fluff_key = i.get("full_name") or i.get("name") or ""
                low = fluff_key.lower()
                # Drop evergreen list/learning repos (awesome-*, *-books, etc.)
                if any(w in low for w in GITHUB_NAME_FLUFF):
                    continue
                if not is_gold(
                    i["html_url"],
                    i["name"],
                    i["stargazers_count"],
                    "github",
                    fluff_text=fluff_key,
                ):
                    continue
                # The search already limits repos to the last 30 days, so the story
                # is "this is taking off now": date it when we saw it. Dating it by
                # creation zeroed its freshness and filed it weeks back in the feed.
                created = ""
                if i.get("created_at"):
                    try:
                        created = f" · created {datetime.fromisoformat(i['created_at'].replace('Z', '+00:00')):%b %-d}"
                    except Exception:
                        pass
                results.append({
                    "title": f"{i['name']}: {i['description'] or 'No description'}",
                    "fluff_key": fluff_key,
                    "url": i["html_url"],
                    "snippet": (
                        f"{i['stargazers_count']:,} stars · {i['language'] or 'Multi'} · "
                        f"{i.get('open_issues_count', 0)} issues · "
                        f"{i.get('forks_count', 0)} forks{created}"
                    ),
                    "source": "GitHub",
                    "category": label,
                    "likes": i["stargazers_count"],
                    "published": _now(),
                })
            return results
        except Exception as e:
            print(f"AXON GitHub search error: {e}")
            return []

    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")

    # "Trending" = repos CREATED recently that already pulled real stars, not
    # old giants that merely got a commit this week (the old pushed:> query
    # surfaced freeCodeCamp & friends every run).
    queries = [
        (f"created:>{month_ago} stars:>50", "Momentum"),
        (f"created:>{week_ago} stars:>10", "Momentum"),
        (f"created:>{month_ago} stars:>30 topic:ai", "AI"),
    ]

    results: list[list[dict]] = []
    for q, cat in queries:
        res = await search_github(q, cat)
        results.append(res)
        await asyncio.sleep(1.0)

    seen_urls: set[str] = set()
    for batch in results:
        for item in batch:
            if item["url"] not in seen_urls:
                signals.append(item)
                seen_urls.add(item["url"])

    # One repo per owner: star-farmed sibling repos (x-craft, y-craft, z-craft)
    # would otherwise take every GitHub slot. Keep each owner's most-starred repo.
    best_by_owner: dict[str, dict] = {}
    for item in signals:
        owner = item["fluff_key"].split("/")[0].lower()
        if owner not in best_by_owner or item["likes"] > best_by_owner[owner]["likes"]:
            best_by_owner[owner] = item
    signals = list(best_by_owner.values())

    # Fallback if primary queries returned nothing
    if not signals:
        # Progressively looser, but still creation-date scoped so we never fall
        # back to all-time-famous repos just to fill the feed.
        fallback_queries = [
            (f"created:>{month_ago} stars:>20 topic:ai", "AI"),
            (f"created:>{month_ago} stars:>10", "Momentum"),
            (f"created:>{week_ago} stars:>3", "Momentum"),
        ]
        for q, cat in fallback_queries:
            batch = await search_github(q, cat)
            for item in batch:
                if item["url"] not in seen_urls:
                    signals.append(item)
                    seen_urls.add(item["url"])
            if signals:
                break
            await asyncio.sleep(1.0)

    return signals


# ---------------------------------------------------------------------------
# TOOLS & LAUNCHES — things you can actually try
# ---------------------------------------------------------------------------

async def hunt_product_launches(client: httpx.AsyncClient):
    """Product Hunt daily top products + tech-focused launch feeds."""
    feeds = [
        ("ProductHunt", "https://www.producthunt.com/feed"),
    ]
    signals = []
    for name, url in feeds:
        try:
            res = await client.get(url, timeout=12.0, follow_redirects=True)
            feed = feedparser.parse(res.text)
            for e in feed.entries[:12]:
                title = e.get("title", "")
                if not title:
                    continue
                signals.append({
                    "title": title,
                    "url": e.link,
                    "snippet": (e.get("summary") or "")[:400],
                    "source": name,
                    "category": "Discovery",
                    "likes": 0,
                    "published": _parse_feed_date(e),
                })
        except Exception:
            continue
    return signals


# ---------------------------------------------------------------------------
# AI LABS — model releases and announcements
# ---------------------------------------------------------------------------

async def hunt_ai_labs(client: httpx.AsyncClient):
    """RSS feeds from major AI labs and companies. (Anthropic has no RSS — it's
    handled separately via its sitemap in hunt_anthropic.)"""
    feeds = [
        ("OpenAI", "https://openai.com/news/rss.xml"),
        ("DeepMind", "https://deepmind.google/blog/rss.xml"),
        ("GoogleAI", "https://blog.google/technology/ai/rss/"),
        ("HuggingFace", "https://huggingface.co/blog/feed.xml"),
    ]
    signals = []
    for name, url in feeds:
        try:
            res = await client.get(url, timeout=10.0, follow_redirects=True)
            feed = feedparser.parse(res.text)
            _check_feed(name, feed.entries)
            for e in feed.entries[:8]:
                signals.append({
                    "title": e.title,
                    "url": e.link,
                    "snippet": (e.get("summary") or "")[:400],
                    "source": name,
                    "category": "AI",
                    "likes": 0,
                    "published": _parse_feed_date(e),
                })
        except Exception:
            continue
    return signals


async def hunt_anthropic(client: httpx.AsyncClient):
    """Anthropic publishes no RSS feed, but robots.txt allows crawling and its
    sitemap.xml lists every /news/ page with a lastmod date. We take the newest
    pages and read og:title + meta description from each for a clean card."""
    try:
        res = await client.get(
            "https://www.anthropic.com/sitemap.xml", timeout=12.0, follow_redirects=True
        )
        if res.status_code != 200:
            _check_feed("Anthropic", [])
            return []
        entries = re.findall(
            r"<loc>(https://www\.anthropic\.com/news/[^<]+)</loc>\s*(?:<lastmod>([^<]+)</lastmod>)?",
            res.text,
        )
        newest = sorted(
            ((u, _parse_sitemap_date(d)) for u, d in entries if d),
            key=lambda x: x[1],
            reverse=True,
        )[:8]
        _check_feed("Anthropic", newest)

        async def fetch_meta(url: str, pub: datetime):
            try:
                r = await client.get(url, timeout=12.0, follow_redirects=True)
                page = r.text
                og = re.search(
                    r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"', page, re.I
                )
                desc = re.search(
                    r'<meta[^>]+name="description"[^>]+content="([^"]+)"', page, re.I
                )
                title = (
                    html.unescape(og.group(1)).strip()
                    if og
                    else url.rstrip("/").rsplit("/", 1)[-1].replace("-", " ").title()
                )
                snippet = html.unescape(desc.group(1)).strip()[:400] if desc else title
                return {
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "source": "Anthropic",
                    "category": "AI",
                    "likes": 0,
                    "published": pub,
                }
            except Exception:
                return None

        results = await asyncio.gather(*[fetch_meta(u, p) for u, p in newest])
        return [r for r in results if r]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# INFRASTRUCTURE — hardware and scaling layer
# ---------------------------------------------------------------------------

async def hunt_infrastructure(client: httpx.AsyncClient):
    """Blog feeds from infra/compute providers."""
    # NOTE: Pinecone / Modal / Cerebras have no working RSS feed (all 404) —
    # replaced with verified-live compute/infra + research feeds.
    feeds = [
        ("NVIDIA", "https://developer.nvidia.com/blog/feed/"),
        ("Together", "https://www.together.ai/blog/rss.xml"),
        ("GoogleResearch", "https://research.google/blog/rss/"),
    ]
    signals = []
    for name, url in feeds:
        try:
            res = await client.get(url, timeout=12.0, follow_redirects=True)
            feed = feedparser.parse(res.text)
            _check_feed(name, feed.entries)
            for e in feed.entries[:5]:
                signals.append({
                    "title": e.title,
                    "url": e.link,
                    "snippet": (e.get("summary") or "")[:400],
                    "source": name,
                    "category": "AI",
                    "likes": 0,
                    "published": _parse_feed_date(e),
                })
        except Exception:
            continue
    return signals


# ---------------------------------------------------------------------------
# EXPERT BLOGS — personal signals from elite engineers
# ---------------------------------------------------------------------------

async def hunt_expert_blogs(client: httpx.AsyncClient):
    """RSS from top engineers and researchers."""
    # Cut the stale, rarely-updated blogs (Karpathy/Altman/Fast.ai/BAIR/LilianWeng
    # were months-to-a-year out of date — dead weight). Keep only consistently
    # fresh, high-signal voices; the global FRESHNESS_DAYS gate keeps even these honest.
    experts = [
        ("SimonW", "https://simonwillison.net/atom/everything/"),
    ]
    signals = []
    for name, url in experts:
        try:
            res = await client.get(url, timeout=12.0, follow_redirects=True)
            feed = feedparser.parse(res.text)
            _check_feed(name, feed.entries)
            for e in feed.entries[:3]:
                signals.append({
                    "title": e.title,
                    "url": e.link,
                    "snippet": (e.get("summary") or "")[:400],
                    "source": name,
                    "category": "Momentum",
                    "likes": 0,
                    "published": _parse_feed_date(e),
                })
        except Exception:
            continue
    return signals


# ---------------------------------------------------------------------------
# LOBSTERS — high-signal technical community
# ---------------------------------------------------------------------------

async def hunt_lobsters(client: httpx.AsyncClient):
    """Lobste.rs top technical discussions."""
    try:
        res = await client.get("https://lobste.rs/hottest.json", timeout=10.0)
        items = res.json()[:12]
        results = []
        for i in items:
            pub = _now()
            if i.get("created_at"):
                try:
                    pub = datetime.fromisoformat(i["created_at"].replace("Z", "+00:00"))
                except Exception:
                    pass
            results.append({
                "title": i["title"],
                "url": i.get("url") or i["short_id_url"],
                "snippet": (i.get("description") or i["title"])[:300],
                "source": "Lobsters",
                "category": "Concerns",
                "likes": i.get("score", 0),
                "published": pub,
            })
        return results
    except Exception:
        try:
            res = await client.get("https://lobste.rs/rss", timeout=10.0)
            feed = feedparser.parse(res.text)
            return [
                {
                    "title": e.title,
                    "url": e.link,
                    "snippet": (e.get("summary") or "")[:300],
                    "source": "Lobsters",
                    "category": "Concerns",
                    "likes": 0,
                    "published": _parse_feed_date(e),
                }
                for e in feed.entries[:15]
            ]
        except Exception:
            return []


# ---------------------------------------------------------------------------
# ARXIV — research papers
# ---------------------------------------------------------------------------

async def hunt_arxiv(client: httpx.AsyncClient):
    """Latest cs.AI and cs.LG papers from ArXiv.

    Uses the RSS feeds (rss.arxiv.org), NOT the legacy export API query endpoint:
    export.arxiv.org/api/query now returns HTTP 429 (rate-limited) for shared /
    cloud IPs like Render's, which the old code silently swallowed as an empty
    result — that's why ArXiv kept going stale. The RSS feeds aren't throttled.
    """
    feeds = [
        "https://rss.arxiv.org/rss/cs.AI",
        "https://rss.arxiv.org/rss/cs.LG",
    ]
    signals: list[dict] = []
    seen: set[str] = set()
    for url in feeds:
        try:
            res = await client.get(url, timeout=20.0)
            if res.status_code != 200:
                print(f"AXON ArXiv: HTTP {res.status_code} for {url}")
                continue
            feed = feedparser.parse(res.text)
            _check_feed("ArXiv", feed.entries)
            for e in feed.entries[:12]:
                # Only genuinely new announcements — skip 'replace' (updates to old
                # papers) so we don't resurface stale work with a fresh announce date.
                atype = (e.get("arxiv_announce_type") or "").lower()
                if atype and atype not in ("new", "cross"):
                    continue
                link = e.get("link")
                if not link or link in seen:
                    continue
                seen.add(link)
                # RSS summary is prefixed "arXiv:xxxx Announce Type: new \nAbstract:";
                # strip down to the abstract for a clean snippet.
                summary = e.get("summary", "")
                m = re.search(r"Abstract:\s*(.*)", summary, re.S)
                clean = (m.group(1) if m else summary).replace("\n", " ").strip()
                signals.append({
                    "title": e.title.replace("\n", " ").strip(),
                    "url": link,
                    "snippet": clean[:500],
                    "source": "ArXiv",
                    "category": "Signal",
                    "likes": 0,
                    "published": _parse_feed_date(e),
                })
        except Exception as ex:
            print(f"AXON ArXiv error for {url}: {ex}")
            continue
    return signals


# ---------------------------------------------------------------------------
# TECH NEWS RSS — broader tech/AI coverage
# ---------------------------------------------------------------------------

async def hunt_tech_news(client: httpx.AsyncClient):
    """Curated tech news feeds focused on AI and developer tools."""
    feeds = [
        ("TechCrunch", "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ("TheVerge", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
        ("ArsTechnica", "https://feeds.arstechnica.com/arstechnica/technology-lab"),
    ]
    signals = []
    for name, url in feeds:
        try:
            res = await client.get(url, timeout=12.0, follow_redirects=True)
            feed = feedparser.parse(res.text)
            for e in feed.entries[:6]:
                signals.append({
                    "title": e.title,
                    "url": e.link,
                    "snippet": (e.get("summary") or "")[:400],
                    "source": name,
                    "category": "AI",
                    "likes": 0,
                    "published": _parse_feed_date(e),
                })
        except Exception:
            continue
    return signals


# ===========================================================================
# SCORING & ENRICHMENT
# ===========================================================================

def _score_signals(signals: list[dict]) -> None:
    """Attach an engagement_score to each signal in place.

    score = source_weight * (0.55 * engagement + 0.45 * recency)
      - engagement: the item's rank by likes *within its own source* this run,
        0 = bottom, 1 = top, ties share the middle. Ranks make GitHub stars and
        HN points comparable, one viral outlier can't squash the rest, and a
        source with no vote counts (RSS, likes == 0) ties at a neutral 0.5
        instead of being capped below every voted source.
      - recency: exponential decay on article age (~3-day scale).
    """
    now = _now()
    likes_by_source: dict[str, list[int]] = {}
    for s in signals:
        likes_by_source.setdefault(s["source"].lower(), []).append(s.get("likes", 0) or 0)
    for likes in likes_by_source.values():
        likes.sort()

    for s in signals:
        src = s["source"].lower()
        likes = likes_by_source[src]
        mine = s.get("likes", 0) or 0
        n = len(likes)
        if n == 1:
            norm_eng = 0.5
        else:
            below = bisect.bisect_left(likes, mine)
            ties = bisect.bisect_right(likes, mine) - below - 1
            norm_eng = (below + 0.5 * ties) / (n - 1)

        pub = s.get("published") or now
        age_hours = max(0.0, (now - pub).total_seconds() / 3600)
        recency = math.exp(-age_hours / RECENCY_SCALE_HOURS)

        weight = SOURCE_WEIGHTS.get(src, 1.0)
        s["norm_eng"] = round(norm_eng, 5)
        s["recency"] = round(recency, 5)
        s["score"] = round(weight * (0.55 * norm_eng + 0.45 * recency), 5)


def _raise_kept_score(article: Article, sig: dict) -> bool:
    """Move a kept story up when the same link comes back with more points.

    Only the traction half can change, and only upward. The freshness stored
    at ingest stays put, so a later sweep cannot age the score down. Stories
    saved before that field existed lock freshness on the first bump, then
    stop aging too. Returns True when the row changed and needs a commit.
    """
    likes_now = int(sig.get("likes") or 0)
    if likes_now <= int(article.likes or 0):
        return False
    weight = SOURCE_WEIGHTS.get((article.source or "").lower(), 1.0)
    norm = float(sig.get("norm_eng", 0.5))
    if article.score_recency is None:
        article.score_recency = float(sig.get("recency") or 0.0)
    new_score = round(weight * (0.55 * norm + 0.45 * float(article.score_recency)), 5)
    article.likes = likes_now
    if new_score > float(article.engagement_score or 0.0):
        article.engagement_score = new_score
    return True


# Title-overlap threshold for treating two cross-source items as the same story.
DEDUP_JACCARD = 0.6
_DEDUP_STOP = {
    "the", "a", "an", "and", "or", "for", "with", "new", "how", "why",
    "this", "that", "from", "via", "your", "you", "are", "now", "its",
}


def _title_fingerprint(title: str) -> set[str]:
    """Significant word set of a title, for near-duplicate comparison."""
    toks = re.findall(r"[a-z0-9]+", (title or "").lower())
    return {t for t in toks if len(t) > 2 and t not in _DEDUP_STOP}


def _is_near_dup(tokens: set[str], source: str, accepted: list[tuple[str, set[str]]]) -> bool:
    """True if `tokens` strongly overlaps an already-accepted item from a
    DIFFERENT source (the 'same story syndicated across feeds' case). Same-source
    overlap is left alone — those are usually genuinely distinct posts."""
    if not tokens:
        return False
    for src, prev in accepted:
        if src == source or not prev:
            continue
        union = len(tokens | prev)
        if union and len(tokens & prev) / union >= DEDUP_JACCARD:
            return True
    return False


async def _hydrate_full_content(client: httpx.AsyncClient, articles: list[dict]) -> None:
    """Fetch readable body text for selected articles in place (best-effort).

    Aggregator domains are skipped inside extract_article_content (their snippet
    is already the payload), so this mostly hits the blog/news long-form sources
    whose RSS summary is too thin for a good AI insight.
    """
    sem = asyncio.Semaphore(FULL_CONTENT_CONCURRENCY)

    async def one(sig: dict) -> None:
        url = sig.get("url")
        if not url:
            return
        async with sem:
            try:
                text = await extract_article_content(url)
                if text:
                    sig["full_content"] = text
            except Exception:
                pass

    await asyncio.gather(*[one(s) for s in articles])


# ===========================================================================
# MAIN INGESTION
# ===========================================================================

async def ingest_intelligence(session: Session, context_id: str | None = None):
    print(f"AXON: Scanning sources (Context: {context_id or 'ALL'})...")
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        if context_id == "GitHub":
            tasks = [hunt_github_trending(client)]
        elif context_id == "AI":
            tasks = [hunt_ai_labs(client), hunt_anthropic(client), hunt_tech_news(client), hunt_infrastructure(client)]
        elif context_id == "Discovery":
            tasks = [hunt_product_launches(client), hunt_hn_discussions(client)]
        elif context_id == "Signal":
            tasks = [hunt_arxiv(client)]
        else:
            tasks = [
                hunt_hn_top(client),
                hunt_hn_discussions(client),
                hunt_github_trending(client),
                hunt_product_launches(client),
                hunt_ai_labs(client),
                hunt_anthropic(client),
                hunt_infrastructure(client),
                hunt_expert_blogs(client),
                hunt_lobsters(client),
                hunt_arxiv(client),
                hunt_tech_news(client),
            ]
        results = await asyncio.gather(*tasks)

        raw_signals: list[dict] = []
        for batch in results:
            raw_signals.extend(batch)

        # Rank by computed engagement_score (normalized engagement + recency *
        # source weight) so genuinely high-signal items win the per-source/total
        # caps, instead of the old random.shuffle lottery.
        _score_signals(raw_signals)
        raw_signals.sort(key=lambda s: s.get("score", 0.0), reverse=True)

        # Only check the URLs we actually fetched against the DB, instead of
        # loading every existing URL into memory (which grows unbounded).
        candidate_urls = {s.get("url") for s in raw_signals if s.get("url")}
        existing_by_url = (
            {
                article.url: article
                for article in session.exec(
                    select(Article).where(col(Article.url).in_(candidate_urls))
                ).all()
            }
            if candidate_urls
            else {}
        )
        final: list[dict] = []
        seen: set[str] = set()
        source_counts: dict[str, int] = {}
        accepted_fingerprints: list[tuple[str, set[str]]] = []
        freshness_cutoff = _now() - timedelta(days=FRESHNESS_DAYS)
        raised = 0

        for sig in raw_signals:
            url = sig.get("url")
            source = sig["source"]
            engagement = sig.get("likes", 0)
            if not url or url in seen:
                continue
            if url in existing_by_url:
                if _raise_kept_score(existing_by_url[url], sig):
                    raised += 1
                continue
            # Freshness gate: never let stale RSS or resurfaced old threads enter.
            pub = sig.get("published")
            if pub is not None:
                if pub.tzinfo is None:
                    pub = pub.replace(tzinfo=timezone.utc)
                if pub < freshness_cutoff:
                    continue
            fluff_key = sig.get("fluff_key")
            if not is_gold(url, sig["title"], engagement, source, fluff_text=fluff_key):
                continue
            # Collapse the same story arriving from multiple feeds in one run.
            # raw_signals is score-sorted, so the highest-scored copy is kept.
            tokens = _title_fingerprint(sig.get("title", ""))
            if _is_near_dup(tokens, source, accepted_fingerprints):
                continue
            if len(final) >= MAX_TOTAL_PER_RUN:
                # Still walk the rest of the sweep so a link we already kept can
                # pick up a higher point count. New admits stay capped at 20.
                continue
            source_counts[source] = source_counts.get(source, 0) + 1
            if source_counts[source] > MAX_PER_SOURCE:
                continue
            final.append(sig)
            seen.add(url)
            accepted_fingerprints.append((source, tokens))

        # Record what each source actually returned this run (before/after the
        # dedupe + per-source caps), so the admin dashboard can tell "GitHub
        # fetched 0 today" apart from "GitHub just hasn't published".
        raw_by_source = Counter(s["source"] for s in raw_signals)
        ingested_by_source = Counter(s["source"] for s in final)
        last_fetch_report["at"] = _now().isoformat()
        last_fetch_report["raw"] = len(raw_signals)
        last_fetch_report["ingested"] = len(final)
        last_fetch_report["sources"] = {
            src: {"raw": raw_by_source.get(src, 0), "ingested": ingested_by_source.get(src, 0)}
            for src in sorted(set(raw_by_source) | set(ingested_by_source))
        }

        if raised:
            session.commit()
        if not final:
            if raised:
                print(f"AXON: Raised {raised} stored scores")
            return 0

        # Pull readable long-form text for the selected articles so the AI writes
        # insights from the real body, not a 1-2 sentence RSS blurb.
        await _hydrate_full_content(client, final)

        added = 0
        for sig in final:
            # Classify ONCE, here, as the single source of truth. (The analyzer
            # no longer re-classifies — the per-hunter category hints were only
            # ever a fallback and used to get silently overwritten downstream.)
            category = classify_article(sig["title"], sig["url"], sig["source"])
            article = Article(
                title=sig["title"],
                url=sig["url"],
                source=sig["source"],
                published_date=sig.get("published", _now()),
                content_snippet=sig.get("snippet", ""),
                full_content=sig.get("full_content"),
                category=category,
                likes=sig.get("likes", 0),
                engagement_score=sig.get("score", 0.0),
                score_recency=sig.get("recency"),
            )
            try:
                session.add(article)
                session.flush()
                added += 1
            except Exception:
                session.rollback()

        session.commit()
        if raised:
            print(f"AXON: Raised {raised} stored scores")
        print(f"AXON: Ingested {added} signals from {len(source_counts)} sources")
        return added
