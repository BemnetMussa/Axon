import os
import httpx
import asyncio
import feedparser
import re
import html
from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.models import Article
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

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

MAX_PER_SOURCE = 15


def is_gold(url: str, title: str, engagement: int = 0, source: str = "") -> bool:
    try:
        threshold = VIRAL_THRESHOLDS.get(source.lower(), 0)
        if threshold and engagement >= threshold:
            return True
        domain = url.split("/")[2].replace("www.", "")
        if any(bad in domain for bad in DOMAIN_BLACKLIST):
            return False
        if any(w in title.lower() for w in TITLE_FLUFF):
            return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# HACKER NEWS — top stories (what people are actually talking about)
# ---------------------------------------------------------------------------

async def hunt_hn_top(client: httpx.AsyncClient):
    """Fetch the current HN front-page stories with their point counts."""
    try:
        res = await client.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10.0
        )
        story_ids = res.json()[:35]

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
                return {
                    "title": item.get("title", ""),
                    "url": url,
                    "snippet": item.get("text", "")[:400] or item.get("title", ""),
                    "source": "HackerNews",
                    "category": "General",
                    "likes": item.get("score", 0),
                }
            except Exception:
                return None

        stories = await asyncio.gather(*[fetch_story(sid) for sid in story_ids])
        return [s for s in stories if s and s["title"]]
    except Exception:
        return []


async def hunt_hn_discussions(client: httpx.AsyncClient):
    """Ask HN / Show HN — community discussions and launches."""
    url = "https://hn.algolia.com/api/v1/search?tags=(ask_hn,show_hn)&numericFilters=num_comments>5&hitsPerPage=30"
    try:
        res = await client.get(url, timeout=10.0)
        hits = res.json().get("hits", [])
        return [
            {
                "title": h["title"],
                "url": f"https://news.ycombinator.com/item?id={h['objectID']}",
                "snippet": (h.get("story_text") or "")[:300] or h["title"],
                "source": "HackerNews",
                "category": "Discovery" if "show hn" in h["title"].lower() else "Concerns",
                "likes": h.get("points", 0),
            }
            for h in hits
        ]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# GITHUB — actually trending repos
# ---------------------------------------------------------------------------

async def hunt_github_trending(client: httpx.AsyncClient):
    """Multiple GitHub search strategies to surface genuinely trending repos."""
    gh_headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    signals: list[dict] = []

    async def search_github(query: str, label: str):
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=20"
        try:
            res = await client.get(url, headers=gh_headers, timeout=15.0)
            if res.status_code != 200:
                return []
            items = res.json().get("items", [])
            return [
                {
                    "title": f"{i['name']}: {i['description'] or 'No description'}",
                    "url": i["html_url"],
                    "snippet": (
                        f"{i['stargazers_count']:,} stars · {i['language'] or 'Multi'} · "
                        f"{i.get('open_issues_count', 0)} issues · "
                        f"{i.get('forks_count', 0)} forks"
                    ),
                    "source": "GitHub",
                    "category": label,
                    "likes": i["stargazers_count"],
                }
                for i in items
                if is_gold(i["html_url"], i["name"], i["stargazers_count"], "github")
            ]
        except Exception:
            return []

    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    queries = [
        (f"created:>{week_ago} stars:>50", "Momentum"),
        (f"created:>{month_ago} stars:>200 topic:ai", "AI"),
        (f"created:>{month_ago} stars:>200 topic:machine-learning", "AI"),
        (f"created:>{month_ago} stars:>100 (cli OR tool OR app OR framework OR sdk)", "Discovery"),
        (f"pushed:>{week_ago} stars:>1000 topic:llm", "AI"),
    ]

    results = await asyncio.gather(*[search_github(q, cat) for q, cat in queries])
    seen_urls: set[str] = set()
    for batch in results:
        for item in batch:
            if item["url"] not in seen_urls:
                signals.append(item)
                seen_urls.add(item["url"])

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
        items = res.json()[:20]
        return [
            {
                "title": i["title"],
                "url": i.get("url") or i["short_id_url"],
                "snippet": (i.get("description") or i["title"])[:300],
                "source": "Lobsters",
                "category": "Concerns",
                "likes": i.get("score", 0),
            }
            for i in items
        ]
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
        "search_query=cat:cs.AI+OR+cat:cs.LG&sortBy=submittedDate&max_results=30"
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
                })
        except Exception:
            continue
    return signals


# ===========================================================================
# MAIN INGESTION
# ===========================================================================

async def ingest_intelligence(session: Session):
    print("AXON: Scanning all sources...")
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
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
            if not is_gold(url, sig["title"], engagement, source):
                continue
            source_counts[source] = source_counts.get(source, 0) + 1
            if source_counts[source] > MAX_PER_SOURCE:
                continue
            final.append(sig)
            seen.add(url)

        if not final:
            return 0

        for sig in final:
            article = Article(
                title=sig["title"],
                url=sig["url"],
                source=sig["source"],
                published_date=datetime.utcnow(),
                content_snippet=sig.get("snippet", ""),
                category=sig.get("category", "General"),
                likes=sig.get("likes", 0),
            )
            session.add(article)

        session.commit()
        print(f"AXON: Ingested {len(final)} signals from {len(source_counts)} sources")
        return len(final)
