# backend/app/main.py
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from sqlmodel import Session
from app.core.database import init_db, get_session
from app.services.fetcher import ingest_data
from app.services.analyzer import analyze_articles 

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"status": "Axon is live 🚀"}

@app.post("/ingest")
async def trigger_ingestion(session: Session = Depends(get_session)):
    count = await ingest_data(session)
    return {"message": "Ingestion complete", "new_articles": count}


@app.post("/analyze")
def trigger_analysis(session: Session = Depends(get_session)):
    count = analyze_articles(session)
    return {"message": "Analysis complete", "articles_processed": count}