"""Community stub for the AI analysis layer.

Prompts, classification, insights, digests, and article chat remain proprietary.
This stub keeps imports working for OSS contributors working on the API shell.
"""

from __future__ import annotations

from sqlmodel import Session

from app.models import Article

_HOSTED = "https://axon-phi-ruby.vercel.app"
_STUB_MSG = (
    f"AI analysis is part of the hosted Axon product. Try it at {_HOSTED} "
    "or install private/services/analyzer.py for a full local engine."
)


def get_last_ai_error() -> str | None:
    return "community-stub: proprietary AI layer not installed"


def get_embed_model():
    return None


def classify_article(title: str, url: str, source: str) -> str:
    _ = title, url, source
    return "general"


def update_trends(session: Session, articles: list[Article]) -> None:
    _ = session, articles


def generate_insight(title: str, content: str, retries: int = 2) -> str:
    _ = title, content, retries
    return _STUB_MSG


def generate_deep_brief(title: str, content: str) -> str:
    _ = title, content
    return _STUB_MSG


def probe_groq() -> dict:
    return {
        "key_present": False,
        "reachable": False,
        "error": "community-stub: proprietary AI layer not installed",
        "mode": "community-stub",
    }


def analyze_articles(session: Session, progress=None) -> int:
    _ = session, progress
    print("AXON: community stub — analyze_articles is a no-op without private/services/analyzer.py")
    return 0


def retry_failed_insights(session: Session, progress=None) -> int:
    _ = session, progress
    return 0


def chat_about_article(title: str, content: str, insight: str, question: str) -> str:
    _ = title, content, insight, question
    return _STUB_MSG


def generate_chat_suggestions(
    title: str, content: str, insight: str | None = None
) -> list[str]:
    _ = title, content, insight
    return [
        "What changed for builders?",
        "Why does this matter now?",
        "What should I watch next?",
    ]


def generate_weekly_digest(session: Session) -> str | None:
    _ = session
    return None
