import os
from groq import Groq
from sqlmodel import Session, select
from app.models import Article
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# backend/app/services/analyzer.py

def classify_article(title: str, url: str, source: str) -> str:
    t, u, s = title.lower(), url.lower(), source.lower()

    if "arxiv" in u or "arxiv" in s or "nature.com" in u or "research" in t or "theory" in t:
        return "Breakthrough"

    if "ask hn" in s or any(w in t for w in ["problem", "issue", "why doesn't", "rant", "sucks", "broken"]):
        return "Problem"
        
    if any(w in t for w in ["ai", "llm", "gpt", "model", "openai", "claude", "weights"]):
        return "AI"
    
    if "github" in u or "github" in s or "show hn" in t or "release" in t or "repo" in t:
        return "Project"
    
    return "Project"# Default to Builder Log if uncaught from these elite sources

def generate_insight(title: str, content: str) -> str:
    if not client.api_key: return "AI Offline. No insight generated."
    prompt = f"Act as a technical startup advisor. In exactly ONE short, punchy sentence, what is the strategic opportunity or technical primitive here? Title: {title}. Content: {content[:500]}"
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=60
        )
        return res.choices[0].message.content.strip().replace('"', '') # type: ignore
    except Exception as e:
        return "Insight generation failed."

def generate_deep_brief(title: str, content: str) -> str:
    prompt = f"Analyze this for a Technical Founder. Break it down into 3 short bullet points: 1. The Technical Primitive. 2. Market Impact. 3. The Build-Opportunity. \nTitle: {title}\nContent: {content}"
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=250
        )
        return res.choices[0].message.content.strip() # type: ignore
    except:
        return "Deep brief generation failed."

def analyze_articles(session: Session):
    articles = session.exec(select(Article).where(Article.is_processed == False)).all()
    for article in articles:
        article.category = classify_article(article.title, article.url, article.source)
        article.insight = generate_insight(article.title, article.content_snippet or "")
        article.is_processed = True
        session.add(article)
    session.commit()
    return len(articles)