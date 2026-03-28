import json
import os
import re
import time
from collections import Counter
from groq import Groq
from sqlmodel import Session, select, col
from app.models import Article, Trend, Digest
from dotenv import load_dotenv

load_dotenv(override=True)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

_embed_model_instance = None

def get_embed_model():
    global _embed_model_instance
    if _embed_model_instance is None:
        import os
        from fastembed import TextEmbedding
        # Vercel requires writing to /tmp
        cache_dir = os.path.join("/tmp", "fastembed_cache")
        os.makedirs(cache_dir, exist_ok=True)
        _embed_model_instance = TextEmbedding(cache_dir=cache_dir)
    return _embed_model_instance

BATCH_SIZE = 8
BATCH_DELAY = 12

def _call_groq_with_fallback(messages: list, max_tokens: int, temperature: float) -> str:
    """Helper to call Groq with a fallback to a smaller, more generous model on rate limit."""
    try:
        res = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return res.choices[0].message.content.strip() # type: ignore
    except Exception as e:
        error_msg = str(e).lower()
        if "rate limit" in error_msg or "too many requests" in error_msg or "429" in error_msg:
            print(f"AXON: Primary model rate limited, falling back to 8B model. Error: {e}")
            fallback_res = client.chat.completions.create(
                messages=messages,
                model="llama3-8b-8192",
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return fallback_res.choices[0].message.content.strip() # type: ignore
        raise e

# ── Categories ──────────────────────────────────────────────
# AI        → Model releases, lab announcements, infrastructure news
# Signal    → Research breakthroughs (ArXiv, academic papers)
# Momentum  → Trending repos, expert builds, rising projects
# Discovery → Tools, frameworks, demos, apps you can try today
# Concerns  → Community problems, debates, discourse


def classify_article(title: str, url: str, source: str) -> str:
    t = title.lower()
    u = url.lower()
    s = source.lower()

    # ── Discovery: tools, launches, things you can try ──────
    if s == "producthunt":
        return "Discovery"

    if "show hn" in t:
        return "Discovery"

    tool_signals = {
        "playground", "demo", "app", "try", "launch", "released",
        "cli", "extension", "plugin", "dashboard", "interface",
        "open source", "self-hosted", "self hosted",
    }
    tool_names = {
        "vllm", "mlx", "unsloth", "llama.cpp", "ollama", "ollama",
        "pytorch", "tensorflow", "langchain", "llamaindex", "gradio",
        "streamlit", "cursor", "v0", "bolt", "replit",
    }
    if any(w in t for w in tool_signals) and "research" not in t and "paper" not in t:
        return "Discovery"
    if any(w in t or w in u for w in tool_names):
        return "Discovery"

    # GitHub repos that look like usable tools
    if s == "github" and any(w in t for w in ["cli", "app", "tool", "sdk", "framework"]):
        return "Discovery"

    # ── Signal: research papers and breakthroughs ───────────
    if s == "arxiv":
        return "Signal"

    research_domains = {"arxiv.org", "nature.com", "science.org", "ieee.org"}
    if any(d in u for d in research_domains):
        return "Signal"

    research_words = {"paper", "study", "findings", "experiment", "benchmark", "evaluation"}
    if any(w in t for w in research_words) and ("arxiv" in u or "research" in t):
        return "Signal"

    # ── Momentum: trending projects, expert voices ──────────
    if s == "github":
        return "Momentum"

    expert_sources = {"karpathy", "simonw", "lilianweng", "altman", "fast.ai"}
    if s in expert_sources:
        return "Momentum"

    if any(w in t for w in ["trending", "rising", "fastest growing", "stars"]):
        return "Momentum"

    # ── AI: lab news, model releases, infrastructure ────────
    ai_labs = {
        "openai", "anthropic", "deepmind", "google", "nvidia",
        "pinecone", "modal", "cerebras", "groq", "mistral",
        "perplexity", "microsoft", "apple", "meta",
    }
    if s in ai_labs or any(lab in u for lab in ai_labs):
        return "AI"

    ai_keywords = {
        "gpt", "llama", "claude", "gemini", "sora", "deepseek",
        "lpu", "cuda", "h100", "b200", "inference", "training",
        "fine-tune", "finetune", "rlhf", "transformer",
    }
    if any(w in t for w in ai_keywords):
        return "AI"

    tech_news = {"techcrunch", "theverge", "arstechnica"}
    if s in tech_news:
        return "AI"

    # ── Concerns: community problems, discourse ─────────────
    if "ask hn" in t:
        return "Concerns"

    if s in {"reddit", "lobsters"}:
        return "Concerns"

    concern_words = {"issue", "broken", "problem", "concern", "risk", "debate", "controversy"}
    if any(w in t for w in concern_words):
        return "Concerns"

    return "AI"


def update_trends(session: Session, articles: list[Article]):
    stop_words = {
        "the", "a", "an", "and", "or", "but", "if", "then", "else", "for",
        "with", "about", "this", "that", "how", "why", "what", "to", "in",
        "on", "at", "is", "are", "was", "were", "new", "engine", "tool",
        "library", "project", "using", "from", "can", "has", "have", "its",
        "not", "more", "into", "via", "part", "adds", "update", "make",
        "will", "get", "been", "also", "just", "like", "when", "which",
        "than", "them", "they", "does", "each", "over", "only", "such",
        "some", "very", "would", "could", "should", "there", "their",
        "your", "based", "first", "most", "other", "after", "before",
    }
    all_text = " ".join(
        f"{a.title} {a.content_snippet or ''}" for a in articles
    ).lower()
    words = re.findall(r"\b[a-z]{4,}\b", all_text)
    keywords = [w for w in words if w not in stop_words]
    counts = Counter(keywords)

    for word, count in counts.most_common(15):
        existing = session.exec(select(Trend).where(Trend.keyword == word)).first()
        if existing:
            existing.count += count
            session.add(existing)
        else:
            session.add(Trend(keyword=word, count=count))
    session.commit()


def generate_insight(title: str, content: str, retries: int = 2) -> str:
    """Two-paragraph insight with retry on rate limit."""
    if not client.api_key:
        return "AI analysis offline."

    clean_content = re.sub(r"<[^>]+>", "", content).strip()[:1000]

    prompt = f"""You are a Lead Intelligence Analyst. Provide a sharp, technical narrative for a technical founder.

Rules:
1. Write exactly 2 cohesive paragraphs.
2. The first paragraph should explain *what* the signal is (the technical reality).
3. The second paragraph should explain *why* it matters and what is interesting/strategic about it.
4. Be direct, dense, and tactical. No conversational filler or "In this article...".
5. No bolding, headers, or lists. Just plain text paragraphs.

Title: {title}
Content: {clean_content}"""

    for attempt in range(retries + 1):
        try:
            content_res = _call_groq_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.4,
            )
            return content_res.replace("**", "").replace("*", "")
        except Exception as e:
            if attempt < retries and "rate" in str(e).lower():
                print(f"AXON: Rate limited on all models, waiting {BATCH_DELAY}s (attempt {attempt + 1})")
                time.sleep(BATCH_DELAY)
            else:
                print(f"AXON INSIGHT ERROR: {e}")
                return ""
    return ""


def generate_deep_brief(title: str, content: str) -> str:
    """Structured 3-part deep brief."""
    clean_content = re.sub(r"<[^>]+>", "", content).strip()[:2000]

    prompt = f"""You are a Lead Intelligence Analyst. Brief a technical founder on this signal:

Title: {title}
Content: {clean_content}

Write a structured brief focusing on hard technical truths and market reality. No bolding. 2-3 sentences per section.

Technical Primitive: (Describe the exact stack shift, architectural change, or hardware requirement. Be highly specific.)

Market Impact: (What does this do to incumbents' moats? How does it affect the cost of intelligence or scale?)

Opportunity: (What concrete product or optimization can a small team build today because of this?)"""

    try:
        content_res = _call_groq_with_fallback(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.5,
        )
        return content_res.replace("**", "")
    except Exception:
        return "Intelligence gathering failed."


def analyze_articles(session: Session):
    articles = session.exec(
        select(Article).where(Article.is_processed == False)  # noqa: E712
    ).all()
    if not articles:
        return 0

    total = len(articles)
    print(f"AXON: Analyzing {total} articles in batches of {BATCH_SIZE}...")

    for i in range(0, total, BATCH_SIZE):
        batch = articles[i:i + BATCH_SIZE]
        for article in batch:
            article.category = classify_article(article.title, article.url, article.source)
            article.insight = generate_insight(article.title, article.content_snippet or "")
            article.is_processed = True
            
            # Generate semantic embedding for the vector search
            if article.insight:
                model = get_embed_model()
                embed_text = f"{article.title} {article.insight}"
                embeddings = list(model.embed([embed_text]))
                if embeddings:
                    article.embedding = embeddings[0].tolist()
                    
            session.add(article)

        session.commit()
        processed = min(i + BATCH_SIZE, total)
        print(f"AXON: Processed {processed}/{total}")

        if i + BATCH_SIZE < total:
            time.sleep(BATCH_DELAY)

    update_trends(session, articles)
    session.commit()
    return total


def retry_failed_insights(session: Session):
    """Re-generate insights for articles that failed on the first pass."""
    failed = session.exec(
        select(Article).where(
            Article.is_processed == True,  # noqa: E712
            (Article.insight == None) | (Article.insight == "") | (Article.insight == "Insight generation failed."),  # noqa: E711
        )
    ).all()
    if not failed:
        return 0

    total = len(failed)
    print(f"AXON: Retrying insights for {total} articles...")
    fixed = 0

    for i in range(0, total, BATCH_SIZE):
        batch = failed[i:i + BATCH_SIZE]
        for article in batch:
            result = generate_insight(article.title, article.content_snippet or "")
            if result:
                article.insight = result
                fixed += 1
                session.add(article)

        session.commit()
        if i + BATCH_SIZE < total:
            time.sleep(BATCH_DELAY)

    print(f"AXON: Fixed {fixed}/{total} insights")
    return fixed


def chat_about_article(title: str, content: str, insight: str, question: str) -> str:
    """Answers a user question about a specific article using its context."""
    if not client.api_key:
        return "AI chat is offline — no API key configured."

    clean_content = re.sub(r"<[^>]+>", "", content).strip()[:1500]

    prompt = f"""You are Axon, an AI tech intelligence assistant. You are helping a builder/founder understand a specific signal.

Article Title: {title}
Context Snippet: {clean_content}
AI Insight: {insight}

User Question: {question}

Provide a concise, expert answer based on the context above. If the context doesn't have enough info, use your general knowledge but stay focused on the implications for the user (founder/developer). Be direct and tactical. No conversational filler."""

    try:
        return _call_groq_with_fallback(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.6,
        )
    except Exception as e:
        print(f"AXON CHAT ERROR: {type(e).__name__}: {e}")
        return f"Chat error: {type(e).__name__}. Check server logs."


def generate_chat_suggestions(
    title: str,
    content_snippet: str,
    insight: str,
    category: str = "",
    source: str = "",
) -> list[str]:
    """Return 4–5 short, article-specific chat starter questions."""
    if not client.api_key:
        return []

    clean = re.sub(r"<[^>]+>", "", content_snippet or "").strip()[:1200]
    ins = re.sub(r"<[^>]+>", "", insight or "").strip()[:800]

    prompt = f"""You are helping a technical founder explore a news signal. Based ONLY on the material below, output exactly 5 short questions they might ask in the chat (max 14 words each). Questions must be specific to THIS story (mention technologies, products, or stakes when relevant). No generic filler.

Title: {title}
Source: {source} | Category: {category}
Snippet: {clean}
Insight: {ins}

Return ONLY a JSON array of 5 strings. No markdown fences, no explanation."""

    try:
        raw = _call_groq_with_fallback(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.45,
        )
        raw = raw.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```\w*\n?", "", raw)
            raw = re.sub(r"\n?```\s*$", "", raw)
        data = json.loads(raw)
        if isinstance(data, list):
            out = [str(x).strip() for x in data[:5] if str(x).strip()]
            return out if len(out) >= 3 else []
    except Exception as e:
        print(f"AXON SUGGESTIONS ERROR: {e}")
    return []


def generate_weekly_digest(session: Session) -> str | None:
    from datetime import datetime, timedelta
    
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    top_articles = session.exec(
        select(Article)
        .where(col(Article.published_date) >= one_week_ago)
        .order_by(col(Article.views).desc())
        .limit(10)
    ).all()
    
    if not top_articles:
        return None
        
    context = "\n".join([f"Title: {a.title}\nInsight: {a.insight}\nSource: {a.source}\n---" for a in top_articles])
        
    prompt = f"""You are the Lead Intelligence Editor for Axon. Write the "Weekly Synthesis" utilizing the following {len(top_articles)} top technical signals:
    
{context}

Your exact output structure MUST be:

## The Big Picture
(1 conclusive, hard-hitting paragraph summarizing the absolute most critical shift or macro trend of the week)

## Core Breakthroughs
* **[Name of Release/Paper]:** (Concise, technical explanation of why it matters)
* **[Name of Release/Paper]:** (Concise, technical explanation of why it matters)
* (list 2 to 4 of the highest-signal items)

## Developer Ecosystem
* (Bullet points linking directly back to the top tools, repos, or frameworks making waves)
* (Highlight specific repositories or libraries mentioned in the signals)

## Key Takeaways
(2 bullet points on what developers should actually care about, learn, or execute on based on this week's intelligence)

Rules: Keep it heavily formatted in pristine Markdown. Never say "Here is the summary". Produce ONLY the final synthesis content block."""

    try:
        content_res = _call_groq_with_fallback(messages=[{"role": "user", "content": prompt}], max_tokens=1000, temperature=0.3)
        digest_content = content_res.strip()
        # Save to database
        digest = Digest(content=digest_content)
        session.add(digest)
        session.commit()
        return digest_content
    except Exception as e:
        print(f"Failed to generate weekly digest: {e}")
        return None
