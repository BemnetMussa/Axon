"""AI analysis entrypoint (open-core).

Loads ``private/services/analyzer.py`` when present; otherwise the community stub.
"""

from app.services._engine import load_engine

_mod = load_engine("analyzer", "app.services.analyzer_community")

get_last_ai_error = _mod.get_last_ai_error
get_embed_model = _mod.get_embed_model
classify_article = _mod.classify_article
update_trends = getattr(_mod, "update_trends", lambda *a, **k: None)
generate_insight = getattr(_mod, "generate_insight", lambda *a, **k: "")
generate_deep_brief = _mod.generate_deep_brief
probe_groq = _mod.probe_groq
analyze_articles = _mod.analyze_articles
retry_failed_insights = _mod.retry_failed_insights
chat_about_article = _mod.chat_about_article
generate_chat_suggestions = _mod.generate_chat_suggestions
generate_weekly_digest = _mod.generate_weekly_digest

__all__ = [
    "get_last_ai_error",
    "get_embed_model",
    "classify_article",
    "update_trends",
    "generate_insight",
    "generate_deep_brief",
    "probe_groq",
    "analyze_articles",
    "retry_failed_insights",
    "chat_about_article",
    "generate_chat_suggestions",
    "generate_weekly_digest",
]
