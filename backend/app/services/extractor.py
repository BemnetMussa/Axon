import re
import httpx
from readability import Document

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

SKIP_DOMAINS = {
    "github.com", "arxiv.org", "news.ycombinator.com",
    "reddit.com", "lobste.rs", "producthunt.com",
}


async def extract_article_content(url: str) -> str | None:
    """Fetch a URL and extract its readable content using readability-lxml."""
    try:
        domain = url.split("/")[2].replace("www.", "")
        if any(skip in domain for skip in SKIP_DOMAINS):
            return None

        async with httpx.AsyncClient(
            headers=HEADERS, follow_redirects=True, timeout=15.0
        ) as client:
            res = await client.get(url)
            if res.status_code != 200:
                return None

        doc = Document(res.text)
        html_content = doc.summary()

        text = re.sub(r"<[^>]+>", " ", html_content)
        text = re.sub(r"&[a-z#0-9]+;", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+", " ", text).strip()

        if len(text) < 100:
            return None

        return text[:8000]
    except Exception:
        return None
