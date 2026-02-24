import os
import httpx
import asyncio
import feedparser
import re
import html
from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.models import Article
from readability import Document
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# SENIOR DECISION: Thresholds for "Viral" bypass
HN_THRESHOLD = 15
GITHUB_THRESHOLD = 200
REDDIT_THRESHOLD = 30
LOBSTERS_THRESHOLD = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

BLACK_LIST = {"medium.com", "dev.to", "facebook.com", "linkedin.com", "designgurus.io", "geeksforgeeks.org", "youtube.com"}

# --- UTILITIES ---

def is_gold(url: str, title: str, engagement: int = 0, source: str = "") -> bool:
    try:
        if source.lower() == "hackernews" and engagement >= HN_THRESHOLD: return True
        if source.lower() == "github" and engagement >= GITHUB_THRESHOLD: return True
        if source.lower() == "reddit" and engagement >= REDDIT_THRESHOLD: return True
        if source.lower() == "lobsters" and engagement >= LOBSTERS_THRESHOLD: return True
        
        domain = url.split('/')[2].replace('www.', '')
        if any(bad in domain for bad in BLACK_LIST): return False
        
        fluff = {"career", "interview", "hired", "salary", "beginner", "roadmap", "job", "tutorial"}
        if any(w in title.lower() for w in fluff): return False
        return True
    except: return False

# --- THE GOLD HUNTERS ---

async def hunt_infrastructure(client: httpx.AsyncClient):
    """INFRASTRUCTURE: Mining the hardware and scaling layer."""
    infra_feeds = [
        ("NVIDIA", "https://developer.nvidia.com/blog/feed/"),
        ("Pinecone", "https://www.pinecone.io/blog/rss.xml"),
        ("Modal", "https://modal.com/blog/rss.xml"),
        ("Cerebras", "https://www.cerebras.net/blog/feed/")
    ]
    signals = []
    for name, url in infra_feeds:
        try:
            res = await client.get(url, timeout=12.0)
            feed = feedparser.parse(res.text)
            for e in feed.entries[:5]:
                signals.append({
                    "title": f"[{name.upper()}] {e.title}",
                    "url": e.link,
                    "snippet": e.get('summary', '')[:400],
                    "source": name,
                    "category": "AI" # Will be re-classified or put in Infra
                })
        except: continue
    return signals

async def hunt_expert_blogs(client: httpx.AsyncClient):
    """ALPHA: Personal signals from Elite Engineers."""
    experts = [
        ("Karpathy", "https://karpathy.github.io/feed.xml"),
        ("SimonW", "https://simonwillison.net/atom/everything/"),
        ("LilianWeng", "https://lilianweng.github.io/feed.xml"),
        ("Fast.ai", "https://www.fast.ai/posts/index.xml"),
        ("Altman", "https://blog.samaltman.com/rss")
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
                    "snippet": e.get('summary', '')[:400],
                    "source": name,
                    "category": "Project"
                })
        except: continue
    return signals

async def hunt_lobsters(client: httpx.AsyncClient):
    """DISCOURSE: High-signal technical community."""
    try:
        res = await client.get("https://lobste.rs/rss", timeout=10.0)
        feed = feedparser.parse(res.text)
        signals = []
        for e in feed.entries[:15]:
            # Simple point extraction from description if available, else default
            signals.append({
                "title": e.title,
                "url": e.link,
                "snippet": e.get('summary', '')[:300],
                "source": "Lobsters",
                "category": "Problem"
            })
        return signals
    except: return []

async def hunt_alpha_github(client: httpx.AsyncClient):
    """ALPHA: Rising technical projects."""
    last_30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    query = f"created:>{last_30} stars:>20 (engine OR compiler OR llm OR tool OR infra OR kernel OR inference)"
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    try:
        res = await client.get(url, headers=headers, timeout=15.0)
        items = res.json().get('items', [])
        return [{
            "title": f"{i['name']}: {i['description'] or 'Technical Repo'}",
            "url": i['html_url'],
            "snippet": f"Stars: {i['stargazers_count']} | {i['language']}",
            "source": "GitHub",
            "category": "Project",
            "likes": i['stargazers_count']
        } for i in items if is_gold(i['html_url'], i['name'], i['stargazers_count'], "github")]
    except: return []

async def hunt_discourse_hn(client: httpx.AsyncClient):
    """DISCOURSE: Technical discussions on HN."""
    url = f"https://hn.algolia.com/api/v1/search?tags=(ask_hn,show_hn)&numericFilters=num_comments>10&hitsPerPage=40"
    try:
        res = await client.get(url, timeout=10.0)
        hits = res.json().get('hits', [])
        return [{
            "title": h['title'],
            "url": f"https://news.ycombinator.com/item?id={h['objectID']}",
            "snippet": h.get('story_text', '')[:300] or h['title'],
            "source": "HackerNews",
            "category": "Problem" if "ask hn" in h['title'].lower() else "Project",
            "likes": h['points']
        } for h in hits]
    except: return []

async def hunt_pulse_rss(client: httpx.AsyncClient):
    """AI PULSE: Model Creators."""
    feeds = [("OpenAI", "https://openai.com/news/rss.xml"), ("DeepMind", "https://deepmind.google/blog/rss.xml"), ("Anthropic", "https://www.anthropic.com/index.xml")]
    signals = []
    for name, url in feeds:
        try:
            res = await client.get(url, timeout=10.0, follow_redirects=True)
            feed = feedparser.parse(res.text)
            for e in feed.entries[:8]:
                signals.append({"title": e.title, "url": e.link, "snippet": e.get('summary', '')[:400], "source": name, "category": "AI"})
        except: continue
    return signals

async def hunt_research_arxiv(client: httpx.AsyncClient):
    """RESEARCH: High volume ArXiv."""
    url = "https://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.LG&sortBy=submittedDate&max_results=40"
    try:
        res = await client.get(url, timeout=15.0)
        feed = feedparser.parse(res.text)
        return [{"title": e.title, "url": e.link, "snippet": e.summary[:500], "source": "ArXiv", "category": "Breakthrough"} for e in feed.entries]
    except: return []

async def ingest_intelligence(session: Session):
    print("🚀 AXON: Deep Mining Infrastructure & Expert Signals...")
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        tasks = [
            hunt_alpha_github(client), hunt_discourse_hn(client), hunt_pulse_rss(client), 
            hunt_research_arxiv(client), hunt_infrastructure(client), hunt_expert_blogs(client),
            hunt_lobsters(client)
        ]
        results = await asyncio.gather(*tasks)
        raw_signals = results[0] + results[1] + results[2] + results[3] + results[4] + results[5] + results[6]

        all_existing_urls = set(session.exec(select(Article.url)).all())
        final_to_save = []
        seen_in_this_batch = set()
        source_counts = {}

        for sig in raw_signals:
            url = sig.get('url'); source = sig['source']; likes = sig.get('likes', 0)
            if not url or url in all_existing_urls or url in seen_in_this_batch: continue
            if not is_gold(url, sig['title'], likes, source): continue
            source_counts[source] = source_counts.get(source, 0) + 1
            if source_counts[source] > 10: continue 
            final_to_save.append(sig)
            seen_in_this_batch.add(url)

        if not final_to_save: return 0
        for sig in final_to_save:
            article = Article(title=sig['title'], url=sig['url'], source=sig['source'], published_date=datetime.utcnow(), content_snippet=sig['snippet'], category=sig['category'], likes=likes)
            session.add(article)
        session.commit()
        return len(final_to_save)
