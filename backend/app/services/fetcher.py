import os
import httpx
import asyncio
import feedparser
import re
import html
import random
from datetime import datetime, timedelta, timezone
from time import mktime
from sqlmodel import Session, select
from app.models import Article
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# "bearer" for fine-grained PATs, "token" for classic PATs (default)
GITHUB_AUTH_STYLE = (os.getenv("GITHUB_AUTH_STYLE") or "token").strip().lower()

VIRAL_THRESHOLDS = {
    "hackernews": 15,
    "github": 100,
    "reddit": 30,
    "lobsters": 10,
    "producthunt": 0,
}

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

MAX_PER_SOURCE = 8
MAX_TOTAL_PER_RUN = 100


def _now() -> datetime:
    return datetime.now(timezone.utc)


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
    """fluff_text: if set, TITLE_FLUFF is checked against this only (e.g. GitHub owner/repo, not description)."""
    try:
        threshold = VIRAL_THRESHOLDS.get(source.lower(), 0)
        if threshold and engagement >= threshold:
            return True
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
    url = "https://hn.algolia.com/api/v1/search?tags=(ask_hn,show_hn)&numericFilters=num_comments>5&hitsPerPage=15"
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
            if res.status_code != 200:
                body = (res.text or "")[:400]
                print(f"AXON GitHub search HTTP {res.status_code} for q={query[:80]}... body={body}")
                return []
            items = res.json().get("items", [])
            results = []
            for i in items:
                fluff_key = i.get("full_name") or i.get("name") or ""
                if not is_gold(
                    i["html_url"],
                    i["name"],
                    i["stargazers_count"],
                    "github",
                    fluff_text=fluff_key,
                ):
                    continue
                pub = _now()
                if i.get("created_at"):
                    try:
                        pub = datetime.fromisoformat(i["created_at"].replace("Z", "+00:00"))
                    except Exception:
                        pass
                results.append({
                    "title": f"{i['name']}: {i['description'] or 'No description'}",
                    "fluff_key": fluff_key,
                    "url": i["html_url"],
                    "snippet": (
                        f"{i['stargazers_count']:,} stars · {i['language'] or 'Multi'} · "
                        f"{i.get('open_issues_count', 0)} issues · "
                        f"{i.get('forks_count', 0)} forks"
                    ),
                    "source": "GitHub",
                    "category": label,
                    "likes": i["stargazers_count"],
                    "published": pub,
                })
            return results
        except Exception as e:
            print(f"AXON GitHub search error: {e}")
            return []

    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")

    queries = [
        (f"pushed:>{week_ago} stars:>500", "Momentum"),
        (f"created:>{month_ago} stars:>500 topic:ai", "AI"),
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

    # Fallback if primary queries returned nothing (strict stars/date)
    if not signals:
        fallback_queries = [
            ("stars:>200 topic:machine-learning", "AI"),
            ("stars:>100 language:Python topic:ai", "Momentum"),
            ("stars:>50 sort:updated", "Momentum"),
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
    """RSS feeds from major AI labs and companies."""
    feeds = [
        ("OpenAI", "https://openai.com/news/rss.xml"),
        ("DeepMind", "https://deepmind.google/blog/rss.xml"),
        ("Anthropic", "https://www.anthropic.com/index.xml"),
    ]
    signals = []
    for name, url in feeds:
        try:
            res = await client.get(url, timeout=10.0, follow_redirects=True)
            feed = feedparser.parse(res.text)
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


# ---------------------------------------------------------------------------
# INFRASTRUCTURE — hardware and scaling layer
# ---------------------------------------------------------------------------

async def hunt_infrastructure(client: httpx.AsyncClient):
    """Blog feeds from infra/compute providers."""
    feeds = [
        ("NVIDIA", "https://developer.nvidia.com/blog/feed/"),
        ("Pinecone", "https://www.pinecone.io/blog/rss.xml"),
        ("Modal", "https://modal.com/blog/rss.xml"),
        ("Cerebras", "https://www.cerebras.net/blog/feed/"),
    ]
    signals = []
    for name, url in feeds:
        try:
            res = await client.get(url, timeout=12.0)
            feed = feedparser.parse(res.text)
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
    experts = [
        ("Karpathy", "https://karpathy.github.io/feed.xml"),
        ("SimonW", "https://simonwillison.net/atom/everything/"),
        ("LilianWeng", "https://lilianweng.github.io/feed.xml"),
        ("Fast.ai", "https://www.fast.ai/posts/index.xml"),
        ("Altman", "https://blog.samaltman.com/rss"),
    ]
    signals = []
    for name, url in experts:
        try:
            res = await client.get(url, timeout=12.0)
            feed = feedparser.parse(res.text)
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
    """Latest cs.AI and cs.LG papers from ArXiv."""
    url = (
        "https://export.arxiv.org/api/query?"
        "search_query=cat:cs.AI+OR+cat:cs.LG&sortBy=submittedDate&max_results=12"
    )
    try:
        res = await client.get(url, timeout=15.0)
        feed = feedparser.parse(res.text)
        return [
            {
                "title": e.title.replace("\n", " ").strip(),
                "url": e.link,
                "snippet": e.summary.replace("\n", " ").strip()[:500],
                "source": "ArXiv",
                "category": "Signal",
                "likes": 0,
                "published": _parse_feed_date(e),
            }
            for e in feed.entries
        ]
    except Exception:
        return []


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
# MAIN INGESTION
# ===========================================================================

async def ingest_intelligence(session: Session, context_id: str | None = None):
    print(f"AXON: Scanning sources (Context: {context_id or 'ALL'})...")
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        if context_id == "GitHub":
            tasks = [hunt_github_trending(client)]
        elif context_id == "AI":
            tasks = [hunt_ai_labs(client), hunt_tech_news(client), hunt_infrastructure(client)]
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

        # Shuffle broadly prevents the earlier sources from dominating the max limits every run
        random.shuffle(raw_signals)

        all_existing_urls = set(session.exec(select(Article.url)).all())
        final: list[dict] = []
        seen: set[str] = set()
        source_counts: dict[str, int] = {}

        for sig in raw_signals:
            url = sig.get("url")
            source = sig["source"]
            engagement = sig.get("likes", 0)
            if not url or url in all_existing_urls or url in seen:
                continue
            fluff_key = sig.get("fluff_key")
            if not is_gold(url, sig["title"], engagement, source, fluff_text=fluff_key):
                continue
            source_counts[source] = source_counts.get(source, 0) + 1
            if source_counts[source] > MAX_PER_SOURCE:
                continue
            if len(final) >= MAX_TOTAL_PER_RUN:
                break
            final.append(sig)
            seen.add(url)

        if not final:
            return 0

        added = 0
        for sig in final:
            article = Article(
                title=sig["title"],
                url=sig["url"],
                source=sig["source"],
                published_date=sig.get("published", _now()),
                content_snippet=sig.get("snippet", ""),
                category=sig.get("category", "General"),
                likes=sig.get("likes", 0),
            )
            try:
                session.add(article)
                session.flush()
                added += 1
            except Exception:
                session.rollback()

        session.commit()
        print(f"AXON: Ingested {added} signals from {len(source_counts)} sources")
        return added
