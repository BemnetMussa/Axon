import os
import re
from collections import Counter
from groq import Groq
from sqlmodel import Session, select
from app.models import Article, Trend
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Category Names (Bemnet's Vision) ─────────────────────
# AI        → AI news, model releases, company announcements
# Signal    → Research breakthroughs (ArXiv, academic)
# Momentum  → Rising projects, GitHub trending, expert builds
# Concerns  → Community problems, tech discourse, HN Ask, Reddit

def classify_article(title: str, url: str, source: str) -> str:
    t, u, s = title.lower(), url.lower(), source.lower()

    # Research breakthroughs (ArXiv, academic journals)
    if any(w in u or w in s for w in ["arxiv", "nature.com", "research"]):
        return "Signal"

    # Rising Projects & Expert Builders → Momentum
    experts = {"karpathy", "simonw", "lilianweng", "altman", "github", "fast.ai"}
    if any(w in s or w in u for w in experts):
        return "Momentum"
    if "show hn" in t or "yc launch" in t:
        return "Momentum"

    # AI labs, model news, infrastructure → AI
    infra_ai = {"openai", "anthropic", "deepmind", "google", "nvidia", "pinecone", "modal", "cerebras", "groq", "mistral"}
    if any(w in s or w in u for w in infra_ai):
        return "AI"
    if any(w in t for w in ["gpt-", "llama-", "claude", "gemini", "sora", "deepseek", "lpu", "cuda", "h100"]):
        return "AI"

    # Community concerns, problems, discourse → Concerns
    if "ask hn" in t or "reddit" in s or "lobsters" in s:
        return "Concerns"

    return "AI"  # Default


def update_trends(session: Session, articles: list[Article]):
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'for', 'with', 'about',
                  'this', 'that', 'how', 'why', 'what', 'to', 'in', 'on', 'at', 'is', 'are', 'was', 'were',
                  'new', 'ai', 'engine', 'tool', 'library', 'project', 'using', 'from', 'can', 'has', 'have',
                  'its', 'not', 'more', 'into', 'via', 'part', 'adds', 'update', 'via', 'make', 'will', 'get'}
    all_text = " ".join([f"{a.title} {a.content_snippet or ''}" for a in articles]).lower()
    words = re.findall(r'\b[a-z]{4,}\b', all_text)
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
    """Generates a 2-3 sentence insight that explains what this is and why it matters."""
    if not client.api_key:
        return "AI analysis offline."
    
    clean_content = re.sub(r'<[^>]+>', '', content).strip()[:600]
    
    prompt = f"""You are a senior tech analyst writing for builders and founders who track AI and emerging tech.
    
Given this article, write 2-3 concise sentences that:
1. State clearly what this is or what happened
2. Explain why it matters for developers/founders
3. Optionally hint at what opportunity or concern it creates

Be specific, not vague. No filler phrases like "this is a great development" or "this marks a significant milestone".
No markdown. No bullet points. Just plain sentences.

Title: {title}
Content: {clean_content}"""

    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=120,
            temperature=0.4
        )
        return res.choices[0].message.content.strip().replace("**", "").replace("*", "")  # type: ignore
    except:
        return "Insight generation failed."


def generate_deep_brief(title: str, content: str) -> str:
    """Generates a structured 3-part deep brief for a specific article."""
    clean_content = re.sub(r'<[^>]+>', '', content).strip()[:2000]
    
    prompt = f"""You are a Senior Intelligence Analyst briefing a technical founder. Analyze this signal:

Title: {title}
Content: {clean_content}

Write a structured brief with exactly these 3 parts. Each part should be 2-3 sentences, specific and actionable. No markdown bolding, no bullet points:

**Technical Primitive:** (What is the exact technical core, mechanism, or shift happening here? Be precise.)

**Market Impact:** (How does this change the competitive landscape or builder opportunity space right now?)

**Opportunity:** (What is one specific, concrete thing a founder or developer could build or do as a result?)"""

    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=400,
            temperature=0.5
        )
        return res.choices[0].message.content.strip().replace("**", "")  # type: ignore
    except:
        return "Intelligence gathering failed."


def analyze_articles(session: Session):
    articles = session.exec(select(Article).where(Article.is_processed == False)).all()
    if not articles:
        return 0
    for article in articles:
        article.category = classify_article(article.title, article.url, article.source)
        article.insight = generate_insight(article.title, article.content_snippet or "")
        article.is_processed = True
        session.add(article)
    update_trends(session, articles)
    session.commit()
    return len(articles)
