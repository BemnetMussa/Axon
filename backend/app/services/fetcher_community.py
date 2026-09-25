"""Community stub for the curation engine.

The hosted Axon product and full ingest pipeline stay proprietary.
This stub keeps the open API bootable and documents the public contract.
Point the UI at the live demo, or drop a private overlay at
``private/services/fetcher.py`` for a full local engine.
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
    """No-op ingest. Install the private overlay or use the hosted product."""
    _ = session, context_id
    last_fetch_report["mode"] = "community-stub"
    print(
        "AXON: community stub — curation engine not bundled. "
        "Use https://axon-phi-ruby.vercel.app or private/services/fetcher.py"
    )
    return 0
