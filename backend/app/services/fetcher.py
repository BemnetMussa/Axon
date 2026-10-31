"""Curation engine entrypoint.

Loads ``backend/engine/fetcher.py`` (see ``_engine.py`` for the search order);
falls back to the community stub if it is missing.
"""

from app.services._engine import load_engine

_mod = load_engine("fetcher", "app.services.fetcher_community")

last_fetch_report = _mod.last_fetch_report
ingest_intelligence = _mod.ingest_intelligence

__all__ = ["last_fetch_report", "ingest_intelligence"]
