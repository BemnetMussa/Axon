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
# Discovery → Usable tools, frameworks, demos, and playgrounds
# Concerns  → Community problems, tech discourse, HN Ask, Reddit

def classify_article(title: str, url: str, source: str) -> str:
    t, u, s = title.lower(), url.lower(), source.lower()

    # Discovery: Usable tools, frameworks, and demos (The "I want to try this" filter)
    tools = {
        "vllm", "mlx", "unsloth", "llama.cpp", "ollama", "pytorch", "tensorflow", 
        "huggingface.co/spaces", "github.com/trending", "playground", "demo", "usable",
        "framework", "library", "tool", "sdk", "api", "inference"
    }
    if any(w in t or w in u for w in tools):
        if "research" not in t and "paper" not in t: # Prioritize usability
            return "Discovery"
    
    if "show hn" in t or "vibe check" in t:
        return "Discovery"

    # Research breakthroughs (ArXiv, academic journals, labs)
    signals = {"arxiv", "nature.com", "research", "deepmind", "anthropic", "openai", "mistral", "meta.com"}
    if any(w in u or w in s for w in signals):
        if any(x in t for x in ["paper", "research", "introducing", "model", "release", "benchmark"]):
            return "Signal"

    # Rising Projects & Expert Builders → Momentum (If not already Discovery)
    experts = {"karpathy", "simonw", "lilianweng", "altman", "github", "fast.ai", "unsloth", "together", "jina"}
    if any(w in s or w in u for w in experts):
        return "Momentum"

    # AI labs, model news, infrastructure → AI
    infra_ai = {"openai", "anthropic", "deepmind", "google", "nvidia", "pinecone", "modal", "cerebras", "groq", "mistral", "perplexity", "microsoft", "apple"}
    if any(w in s or w in u for w in infra_ai):
        return "AI"
    if any(w in t for w in ["gpt-", "llama-", "claude", "gemini", "sora", "deepseek", "lpu", "cuda", "h100", "b200"]):
        return "AI"

    # Community concerns, problems, discourse → Concerns
    if "ask hn" in t or "reddit" in s or "lobsters" in s or "issue" in t or "broken" in t:
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
    """Generates a narrative 2-paragraph insight that explains what this is and why it matters."""
    if not client.api_key:
        return "AI analysis offline."
    
    clean_content = re.sub(r'<[^>]+>', '', content).strip()[:1000]
    
    prompt = f"""You are a Lead Intelligence Analyst. Provide a sharp, technical narrative for a technical founder.
 
Rules:
1. Write exactly 2 cohesive paragraphs.
2. The first paragraph should explain *what* the signal is (the technical reality).
3. The second paragraph should explain *why* it matters and what is interesting/strategic about it.
4. Be direct, dense, and tactical. No conversational filler or "In this article...".
5. No bolding, headers, or lists. Just plain text paragraphs.

Title: {title}
Content: {clean_content}"""

    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=250,
            temperature=0.4
        )
        return res.choices[0].message.content.strip().replace("**", "").replace("*", "")  # type: ignore
    except:
        return "Insight generation failed."


def generate_deep_brief(title: str, content: str) -> str:
    """Generates a structured 3-part deep brief for a specific article."""
    clean_content = re.sub(r'<[^>]+>', '', content).strip()[:2000]
    
    prompt = f"""You are a Lead Intelligence Analyst. Brief a technical founder on this signal:

Title: {title}
Content: {clean_content}

Write a structured brief focusing on hard technical truths and market reality. No bolding. 2-3 sentences per section.

Technical Primitive: (Describe the exact stack shift, architectural change, or hardware requirement. Be highly specific.)

Market Impact: (What does this do to incumbents' moats? How does it affect the cost of intelligence or scale?)

Opportunity: (What concrete product or optimization can a small team build today because of this?)"""

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
def chat_about_article(title: str, content: str, insight: str, question: str) -> str:
    """Answers a user question about a specific article using its context."""
    if not client.api_key:
        return "AI chat offline."
    
    clean_content = re.sub(r'<[^>]+>', '', content).strip()[:1500]
    
    prompt = f"""You are Axon, an AI tech intelligence assistant. You are helping a builder/founder understand a specific signal.
    
Article Title: {title}
Context Snippet: {clean_content}
AI Insight: {insight}

User Question: {question}

Provide a concise, expert answer based on the context above. If the context doesn't have enough info, use your general knowledge but stay focused on the implications for the user (founder/developer). Be direct and tactical. No conversational filler."""

    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=300,
            temperature=0.6
        )
        return res.choices[0].message.content.strip()  # type: ignore
    except Exception as e:
        print(f"Chat error: {e}")
        return "Sorry, I couldn't process that question right now."
