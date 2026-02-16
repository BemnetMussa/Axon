# backend/app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from app.core.database import init_db, get_session
from app.models import Article
from app.services.fetcher import ingest_intelligence # <--- Updated name
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

# --- THE HUNTER ENDPOINT ---
@app.post("/ingest")
async def trigger_ingestion(session: Session = Depends(get_session)):
    # Calling our new 'Intelligence' hunter
    count = await ingest_intelligence(session)
    return {"status": "success", "new_articles": count}

@app.post("/analyze")
def trigger_analysis(session: Session = Depends(get_session)):
    count = analyze_articles(session)
    return {"status": "success", "processed": count}

@app.get("/articles")
def read_articles(limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Article).order_by(Article.published_date.desc()).limit(limit) # type: ignore
    return session.exec(statement).all()

@app.get("/brief/{article_id}")
def get_brief(article_id: int, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article: return {"error": "Not found"}
    brief = generate_deep_brief(article.title, article.content_snippet or "")
    return {"title": article.title, "brief": brief}

@app.get("/trends")
def read_trends():
    return [] # We'll fill this later if needed

@app.get("/")
def health():
    return {"status": "Axon Hunter is Online"}