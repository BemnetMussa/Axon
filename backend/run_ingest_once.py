"""One-shot manual ingest+analyze against the configured DB (Supabase).

Run from backend/ with the venv:  venv/bin/python run_ingest_once.py
Loads .env BEFORE importing the engine so it connects to Supabase, not localhost.
"""
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Must load env before importing app.core.database (engine is built at import time).
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

from app.core.database import get_script_session  # noqa: E402
from app.services.fetcher import ingest_intelligence  # noqa: E402
from app.services.analyzer import analyze_articles  # noqa: E402


async def main() -> None:
    session = get_script_session()
    try:
        print("=== INGEST: scraping all sources ===", flush=True)
        count = await ingest_intelligence(session)
        print(f"=== INGEST DONE: {count} new articles ===", flush=True)

        if count:
            print("=== ANALYZE: generating insights ===", flush=True)
            analyzed = analyze_articles(session)
            print(f"=== ANALYZE DONE: {analyzed} articles analyzed ===", flush=True)
        else:
            print("=== No new articles, skipping analyze ===", flush=True)
    finally:
        session.close()


if __name__ == "__main__":
    asyncio.run(main())
