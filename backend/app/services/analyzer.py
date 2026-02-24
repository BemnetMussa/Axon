import os
import re
from collections import Counter
from groq import Groq
from sqlmodel import Session, select
from app.models import Article, Trend
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def classify_article(title: str, url: str, source: str) -> str:
    """Classifies articles into the four primary quadrants."""
    t, u, s = title.lower(), url.lower(), source.lower()

    # 1. RESEARCH (Breakthroughs)
    if any(w in u or w in s for w in ["arxiv", "nature.com", "research"]):
        return "Breakthrough"
    
    # 2. ALPHA (Rising Projects & Experts)
    # Whitelisted experts and GitHub go here
    experts = {"karpathy", "simonw", "lilianweng", "altman", "github", "fast.ai"}
    if any(w in s or w in u for w in experts):
        return "Project"
    if "show hn" in t or "yc launch" in t:
        return "Project"

    # 3. AI PULSE & INFRA (Model updates & Hard Hardware)
    # Merging Infra into AI Pulse as per Senior's suggestion
    infra_ai = {"openai", "anthropic", "deepmind", "google", "nvidia", "pinecone", "modal", "cerebras", "groq", "mistral"}
    if any(w in s or w in u for w in infra_ai):
        return "AI"
    if any(w in t for w in ["gpt-", "llama-", "claude", "gemini", "sora", "deepseek", "lpu", "cuda", "h100"]):
        return "AI"

    # 4. DISCOURSE (Community & Problems)
    if "ask hn" in t or "reddit" in s or "lobsters" in s:
        return "Problem"
    
    return "AI" # Default fallback

def update_trends(session: Session, articles: list[Article]):
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'for', 'with', 'about', 'this', 'that', 'how', 'why', 'what', 'to', 'in', 'on', 'at', 'is', 'are', 'was', 'were', 'new', 'ai', 'engine', 'tool', 'library', 'project'}
    all_text = " ".join([f"{a.title} {a.content_snippet or ''}" for a in articles]).lower()
    words = re.findall(r'\b[a-z]{3,}\b', all_text)
    keywords = [w for w in words if w not in stop_words]
    counts = Counter(keywords)
    for word, count in counts.most_common(10):
        statement = select(Trend).where(Trend.keyword == word)
        existing = session.exec(statement).first()
        if existing:
            existing.count += count
            session.add(existing)
        else:
            new_trend = Trend(keyword=word, count=count)
            session.add(new_trend)
    session.commit()

def generate_insight(title: str, content: str) -> str:
    if not client.api_key: return "AI Offline."
    prompt = f"Technical Founder persona. Critique this in ONE short, cynical, punchy sentence of <20 words. Focus on the 'why' or a hidden technical flaw. No markdown. Title: {title}. Content: {content[:400]}"
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=60
        )
        insight = res.choices[0].message.content.strip().replace('"', '').replace("**", "") # type: ignore
        return f"◈ {insight}"
    except: return "Insight generation failed."

def generate_deep_brief(title: str, content: str) -> str:
    prompt = f"""
    Act as a Senior Intelligence Officer for Technical Founders. Analyze this signal:
    Title: {title}
    Content: {content[:2000]}

    Format your response EXACTLY like this (no preamble, no markdown bolding like **text**):
    ▶ THE SIGNAL: (1-2 sentences on the exact technical core or hidden shift)
    ◈ THE CONTEXT: (1 sentence on why this matters right now)
    ↳ THE PLAY: (1 provocative, specific move for a builder or founder)
    
    Tone: Punchy, cynical, high-signal.
    """
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=300
        )
        return res.choices[0].message.content.strip().replace("**", "") # type: ignore
    except: return "Intelligence gathering failed."

def analyze_articles(session: Session):
    articles = session.exec(select(Article).where(Article.is_processed == False)).all()
    if not articles: return 0
    for article in articles:
        article.category = classify_article(article.title, article.url, article.source)
        article.insight = generate_insight(article.title, article.content_snippet or "")
        article.is_processed = True
        session.add(article)
    update_trends(session, articles)
    session.commit()
    return len(articles)
