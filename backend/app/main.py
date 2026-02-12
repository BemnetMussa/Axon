# backend/app/main.py
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List
from app.core.database import init_db, get_session
from app.models import Article, Trend
from app.services.fetcher import ingest_data, RSS_FEEDS
from app.services.analyzer import analyze_articles, get_enriched_trends

app = FastAPI(title="Axon Intelligence API")

# 🔌 Senior Move: Enable CORS so Svelte can talk to us!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In prod, we'll limit this
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

# --- ACTION ENDPOINTS ---

@app.post("/ingest")
async def trigger_ingestion(session: Session = Depends(get_session)):
    count = await ingest_data(session)
    return {"status": "success", "new_articles": count}

@app.post("/analyze")
def trigger_analysis(session: Session = Depends(get_session)):
    count = analyze_articles(session)
    return {"status": "success", "processed": count}

# --- DASHBOARD ENDPOINTS (The Contract) ---

@app.get("/trends")
def read_trends(session: Session = Depends(get_session)):
    """Returns the hot topics with velocity."""
    return get_enriched_trends(session)

@app.get("/articles")
def read_articles(
    keyword: str = None,  # type: ignore
    limit: int = 20, 
    session: Session = Depends(get_session)
):
    """Returns articles, optionally filtered by keyword."""
    statement = select(Article).order_by(Article.published_date.desc()).limit(limit) # type: ignore
    if keyword:
        # Simple search in title or snippet
        statement = statement.where(
            (Article.title.ilike(f"%{keyword}%")) | # type: ignore 
            (Article.content_snippet.ilike(f"%{keyword}%")) # type: ignore
        )
    return session.exec(statement).all()

@app.get("/sources")
def get_sources():
    """Returns the list of feeds we are tracking."""
    return {
        "total": len(RSS_FEEDS),
        "list": [f for f in RSS_FEEDS]
    }