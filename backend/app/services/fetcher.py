# backend/app/services/fetcher.py
import asyncio
import httpx
import feedparser
from datetime import datetime
from sqlmodel import Session, select
from app.models import Article

# A few top-tier tech feeds to start
RSS_FEEDS = [
    "https://news.ycombinator.com/rss",
    "http://feeds.feedburner.com/TechCrunch/",
    "https://www.theverge.com/rss/index.xml"
]

async def fetch_feed(client: httpx.AsyncClient, url: str):
    """Async fetch of a single feed."""
    try:
        response = await client.get(url, timeout=10.0)
        return feedparser.parse(response.text)
    except Exception as e:
        print(f"⚠️ Error fetching {url}: {e}")
        return None

def parse_date(entry):
    """Helper to handle messy RSS date formats."""
    # feedparser usually gives us a struct_time
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return datetime(*entry.published_parsed[:6])
    return datetime.utcnow() # Fallback

async def ingest_data(session: Session):
    """
    Main function to fetch all feeds and save new articles to DB.
    """
    print(f"🔄 Starting ingestion for {len(RSS_FEEDS)} feeds...")
    
    async with httpx.AsyncClient() as client:
        tasks = [fetch_feed(client, url) for url in RSS_FEEDS]
        feeds = await asyncio.gather(*tasks)

    new_count = 0
    
    for feed in feeds:
        if not feed or not feed.entries:
            continue
            
        source_name = feed.feed.get('title', 'Unknown Source') # type: ignore
        
        for entry in feed.entries:
            # Check if URL already exists in DB to avoid duplicates
            existing = session.exec(select(Article).where(Article.url == entry.link)).first()
            if existing:
                continue

            article = Article(
                title=entry.title, # type: ignore
                url=entry.link, # type: ignore
                source=source_name,
                published_date=parse_date(entry),
                content_snippet=entry.get('summary', '')[:500] # type: ignore 
            )
            session.add(article)
            new_count += 1
    
    session.commit()
    print(f"✅ Ingestion complete. Saved {new_count} new articles.")
    return new_count