"""Default AI prompts.

The hosted product loads its own prompts from ``prompts_hosted.py`` when that
file exists next to this one (see ``analyzer._load_prompts``). Any replacement
must define the same functions with the same signatures.
"""


def insight(title: str, content: str) -> str:
    return f"""Summarize the following technology article in up to 3 short paragraphs of plain prose.
State its main point and key specifics. Use only what the article says; do not add opinions or implications.

Title: {title}
Source material: {content}"""


def deep_brief(title: str, content: str) -> str:
    return f"""Write a short brief about this technology story with three sections,
2 sentences each: Technical Primitive, Market Impact, Opportunity. No bold text.

Title: {title}
Content: {content}"""


def chat(title: str, content: str, insight: str, question: str) -> str:
    return f"""Answer the user's question about this article, using only the context below, and keep the answer short.
If the context does not cover the question, say so.

Article Title: {title}
Context Snippet: {content}
AI Insight: {insight}

User Question: {question}"""


def chat_suggestions(title: str, source: str, category: str, snippet: str, insight: str) -> str:
    return f"""Suggest 5 short questions (max 14 words each) a reader might ask about this article.

Title: {title}
Source: {source} | Category: {category}
Snippet: {snippet}
Insight: {insight}

Return ONLY a JSON array of 5 strings. No markdown fences, no explanation."""


def weekly_digest(count: int, context: str) -> str:
    return f"""Write a weekly summary in Markdown of these {count} technology stories.
Use these sections: ## The Big Picture, ## Core Breakthroughs, ## Developer Ecosystem, ## Key Takeaways.
Output only the summary.

{context}"""
