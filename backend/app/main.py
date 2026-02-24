from datetime import datetime
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from sqlalchemy import update
from app.core.database import init_db, get_session
from app.models import Article, Trend
from app.services.fetcher import ingest_intelligence
from app.services.analyzer import analyze_articles, generate_deep_brief

app = FastAPI(title="Axon Intelligence Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/ingest")
async def trigger_ingestion(session: Session = Depends(get_session)):
    count = await ingest_intelligence(session)
    return {"status": "success", "new_articles": count}

@app.post("/analyze")
def trigger_analysis(session: Session = Depends(get_session)):
    count = analyze_articles(session)
    return {"status": "success", "processed": count}

@app.get("/articles")
def read_articles(limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Article).order_by(Article.published_date.desc()).limit(limit * 2)
    all_articles = session.exec(statement).all()
    
    reddit_limit = int(limit * 0.3)
    balanced = []
    reddit_count = 0
    
    for a in all_articles:
        if a.source.lower() == "reddit":
            if reddit_count < reddit_limit:
                balanced.append(a)
                reddit_count += 1
        else:
            balanced.append(a)
        if len(balanced) >= limit: break
            
    return balanced

@app.get("/brief/{article_id}")
def get_brief(article_id: int, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article: return {"error": "Not found"}
    brief = generate_deep_brief(article.title, article.content_snippet or "")
    return {"title": article.title, "brief": brief}

@app.post("/articles/{article_id}/view")
def track_view(article_id: int, session: Session = Depends(get_session)):
    # SENIOR DECISION: Atomic increment to prevent lost updates
    stmt = (
        update(Article)
        .where(Article.id == article_id)
        .values(views=Article.views + 1, last_viewed=datetime.utcnow())
    )
    session.execute(stmt)
    session.commit()
    return {"status": "success"}

@app.get("/trends")
def read_trends(session: Session = Depends(get_session)):
    statement = select(Trend).order_by(Trend.count.desc()).limit(10)
    results = session.exec(statement).all()
    return [{"keyword": t.keyword, "count": t.count, "velocity": "Rising", "is_new": True} for t in results]

@app.get("/")
def health():
    return {"status": "Axon Hunter is Online"}
