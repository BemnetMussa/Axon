"""Curation engine entrypoint (open-core).

Loads ``private/services/fetcher.py`` when present; otherwise the community stub.
"""

from app.services._engine import load_engine

_mod = load_engine("fetcher", "app.services.fetcher_community")

last_fetch_report = _mod.last_fetch_report
ingest_intelligence = _mod.ingest_intelligence

__all__ = ["last_fetch_report", "ingest_intelligence"]
