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
SERPER_KEY = os.getenv("SERPER_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Headers to prevent being blocked by ArXiv/News sites
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- UTILITIES ---

def clean_text(raw_html: str) -> str:
    """Aggressively strips HTML and junk footers."""
    if not raw_html: return ""
    # Decode HTML entities
    text = html.unescape(raw_html)
    # Remove 'Comments' links
    text = re.sub(r'<a\s+[^>]*>.*?Comments.*?</a>', '', text, flags=re.IGNORECASE)
    # Strip all tags
    text = re.sub(r'<.*?>', '', text)
    return text.strip()

async def get_deep_content(client: httpx.AsyncClient, url: str) -> str:
    """Scrapes the actual webpage if the RSS summary is thin."""
    try:
        response = await client.get(url, timeout=12.0, follow_redirects=True, headers=HEADERS)
        if response.status_code != 200: return ""
        doc = Document(response.text)
        summary_html = doc.summary()
        return clean_text(summary_html)[:800]
    except:
        return ""

# --- THE HUNTERS ---

async def hunt_github(client: httpx.AsyncClient):
    """Quadrant: PROJECTS - Finds top-tier GitHub repos from the last 30 days."""
    last_month = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    # Filter for high-signal repositories (>500 stars)
    url = f"https://api.github.com/search/repositories?q=pushed:>{last_month}+stars:>500&sort=stars&order=desc"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    
    try:
        res = await client.get(url, headers=headers, timeout=15.0)
        items = res.json().get('items', [])
        return [{
            "title": f"{i['name']}: {i['description'] or 'New project'}",
            "url": i['html_url'],
            "snippet": f"Language: {i['language']} | Stars: {i['stargazers_count']}",
            "source": "GitHub",
            "category": "Project"
        } for i in items[:10]]
    except Exception as e:
        print(f"⚠️ GitHub Hunter Error: {e}")
        return []

async def hunt_challenges(client: httpx.AsyncClient):
    """Quadrant: CHALLENGES & FEEDBACK - Hunts for technical friction."""
    signals = []
    
    # 1. Serper Search (Reddit/Forum Rants)
    if SERPER_KEY:
        try:
            search_url = "https://google.serper.dev/search"
            payload = {
                "q": "site:reddit.com OR site:news.ycombinator.com 'unsolved' OR 'bottleneck' OR 'major problem' software engineering",
                "tbs": "qdr:w" # Last week
            }
            res = await client.post(search_url, json=payload, headers={'X-API-KEY': SERPER_KEY}, timeout=15.0)
            for r in res.json().get('organic', []):
                domain = r['link'].split('/')[2].replace('www.', '')
                signals.append({
                    "title": r['title'], "url": r['link'], "snippet": r['snippet'],
                    "source": domain, "category": "Problem"
                })
        except Exception as e:
            print(f"⚠️ Serper Hunter Error: {e}")

    # 2. Ask HN (Hacker News community signals)
    try:
        hn_res = await client.get("https://hnrss.org/ask", timeout=10.0)
        feed = feedparser.parse(hn_res.text)
        for e in feed.entries[:5]:
            signals.append({
                "title": e.title, "url": e.link, "snippet": clean_text(e.summary), # type: ignore 
                "source": "HackerNews", "category": "Problem"
            })
    except: pass
    
    return signals

# --- MASTER INGESTION ---

async def ingest_intelligence(session: Session):
    """Orchestrates the global 4-pillar data sync."""
    print("🚀 AXON: Initiating Global Intelligence Gathering...")
    
    async with httpx.AsyncClient(headers=HEADERS) as client:
        # 1. Parallel fetch from all elite sources
        tasks = [
            hunt_github(client),    # Projects
            hunt_challenges(client), # Challenges
            client.get("https://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.LG&sortBy=submittedDate&max_results=10"), # Breakthroughs
            client.get("https://www.technologyreview.com/topic/artificial-intelligence/feed/"), # AI News
            client.get("https://openai.com/news/rss.xml") # AI News (OpenAI)
        ]
        
        results = await asyncio.gather(*tasks)
        
        raw_signals = results[0] + results[1] # Start with GitHub and Problems

        # 2. Parse Breakthroughs (ArXiv)
        arxiv_feed = feedparser.parse(results[2].text)
        for e in arxiv_feed.entries:
            raw_signals.append({
                "title": e.title, "url": e.link, "snippet": clean_text(e.summary), # type: ignore
                "source": "ArXiv", "category": "Breakthrough"
            })
            
        # 3. Parse AI News (MIT Tech Review & OpenAI)
        for i in [3, 4]:
            feed = feedparser.parse(results[i].text)
            source_name = "MIT Tech" if "technologyreview" in results[i].url.__str__() else "OpenAI"
            for e in feed.entries[:5]:
                raw_signals.append({
                    "title": e.title, "url": e.link, "snippet": clean_text(e.get('summary', '')), # type: ignore
                    "source": source_name, "category": "AI"
                })

        # 4. Filter for NEW items and Deep Scrape
        final_to_save = []
        for sig in raw_signals:
            if not sig.get('url'): continue
            existing = session.exec(select(Article).where(Article.url == sig['url'])).first()
            if existing: continue
            final_to_save.append(sig)

        if not final_to_save:
            print("✅ No new signals found in this cycle.")
            return 0

        print(f"🔍 Deep scanning {len(final_to_save)} new signals for AI analysis...")
        # Concurrent Deep Scrape
        scrape_tasks = [get_deep_content(client, s['url']) for s in final_to_save]
        deep_contents = await asyncio.gather(*scrape_tasks)

        # 5. Commit to Database
        for i, sig in enumerate(final_to_save):
            # Use deep content if original snippet was thin
            content = deep_contents[i] if len(sig['snippet']) < 100 else sig['snippet']
            
            article = Article(
                title=sig['title'],
                url=sig['url'],
                source=sig['source'],
                published_date=datetime.utcnow(),
                content_snippet=content,
                category=sig['category']
            )
            session.add(article)
            
        session.commit()
        print(f"✅ Sync Complete. {len(final_to_save)} items stored in Intelligence Silos.")
        return len(final_to_save)