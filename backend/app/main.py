import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, col
from sqlalchemy import update, func
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.database import init_db, get_session, get_script_session
from app.models import Article, Trend
from app.services.fetcher import ingest_intelligence
from app.services.analyzer import analyze_articles, retry_failed_insights, generate_deep_brief, chat_about_article
from app.services.extractor import extract_article_content

scheduler = AsyncIOScheduler()


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Ingestion & Analysis (manual triggers still available)
# ---------------------------------------------------------------------------

@app.post("/ingest")
async def trigger_ingestion(session: Session = Depends(get_session)):
    count = await ingest_intelligence(session)
    return {"status": "success", "new_articles": count}


@app.post("/analyze")
def trigger_analysis(session: Session = Depends(get_session)):
    count = analyze_articles(session)
    return {"status": "success", "processed": count}


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


@app.post("/articles/{article_id}/chat")
def article_chat(article_id: int, req: ChatRequest, session: Session = Depends(get_session)):
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
# Trends
# ---------------------------------------------------------------------------

@app.get("/trends")
def read_trends(session: Session = Depends(get_session)):
    statement = select(Trend).order_by(col(Trend.count).desc()).limit(10)
    results = session.exec(statement).all()
    return [
        {"keyword": t.keyword, "count": t.count, "velocity": "Rising", "is_new": True}
        for t in results
    ]


@app.get("/")
def health():
    return {"status": "Axon is online", "scheduler": scheduler.running}
