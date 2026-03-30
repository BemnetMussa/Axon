import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

from fastapi import FastAPI, Depends, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from sqlmodel import Session, select, col
from sqlalchemy import update, func
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.database import init_db, get_session, get_script_session
from app.models import Article, Trend, Digest
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

INTERNAL_SECRET = os.getenv("AXON_INTERNAL_SECRET")


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
async def trigger_ingestion(context_id: str | None = Query(default=None), session: Session = Depends(get_session)):
    count = await ingest_intelligence(session, context_id)
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
def article_chat_suggestions(article_id: int, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        return {"error": "Not found", "suggestions": []}
    suggestions = generate_chat_suggestions(
        title=article.title,
        content_snippet=article.content_snippet or "",
        insight=article.insight or "",
        category=article.category,
        source=article.source,
    )
    return {"suggestions": suggestions}


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
# Weekly Digest
# ---------------------------------------------------------------------------

@app.get("/digests/latest")
def get_latest_digest(session: Session = Depends(get_session)):
    digest = session.exec(select(Digest).order_by(col(Digest.created_at).desc()).limit(1)).first()
    if not digest:
        return {"content": "No weekly digest available yet."}
    return {"content": digest.content, "created_at": digest.created_at}

@app.post("/digests/generate")
def trigger_digest(session: Session = Depends(get_session)):
    content = generate_weekly_digest(session)
    return {"status": "success", "digest": content}


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
