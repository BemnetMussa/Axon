"""Fallback stub for the curation engine.

Used only when ``backend/engine/fetcher.py`` is missing (see ``_engine.py``).
Keeps the API bootable and documents the public contract.
"""

from __future__ import annotations

from sqlmodel import Session

last_fetch_report: dict = {
    "at": None,
    "raw": 0,
    "ingested": 0,
    "sources": {},
    "mode": "community-stub",
}


async def ingest_intelligence(session: Session, context_id: str | None = None) -> int:
    """No-op ingest. Restore ``backend/engine/fetcher.py`` for the real pipeline."""
    _ = session, context_id
    last_fetch_report["mode"] = "community-stub"
    print("AXON: community stub — backend/engine/fetcher.py not found, ingest is a no-op")
    return 0
