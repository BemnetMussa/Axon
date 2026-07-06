"""Admin gating, stats shape, ingest cooldown + rate limit, backlog job."""
from datetime import datetime, timezone

import app.main as main
from tests.conftest import make_article


# --- admin gating -----------------------------------------------------------

def test_admin_stats_rejects_non_admin(client, auth_headers):
    assert client.get("/admin/stats", headers=auth_headers).status_code == 403


def test_admin_stats_fails_closed_when_unconfigured(client, admin_headers, monkeypatch):
    monkeypatch.setattr(main, "ADMIN_USER_IDS", set())
    res = client.get("/admin/stats", headers=admin_headers)
    assert res.status_code == 403
    assert "not configured" in res.json()["detail"]


def test_admin_stats_shape(client, admin_headers, session):
    make_article(session, insight="done", is_processed=True)
    make_article(session)  # missing insight

    body = client.get("/admin/stats", headers=admin_headers).json()
    assert body["totals"]["articles"] == 2
    assert body["totals"]["processed"] == 1
    assert body["totals"]["missing_insight"] == 1
    assert body["ai"] == {"key_present": True, "reachable": True, "error": None}
    for key in ("scheduler", "processing", "sources", "daily_volume", "engagement", "recent_runs"):
        assert key in body
    assert len(body["sources"]) == 1
    assert body["sources"][0]["source"] == "HackerNews"


def test_admin_process_reports_already_running(client, admin_headers, monkeypatch):
    monkeypatch.setitem(main._processing, "running", True)
    body = client.post("/admin/process", headers=admin_headers).json()
    assert body["status"] == "already_running"


def test_admin_process_rejects_non_admin(client, auth_headers):
    assert client.post("/admin/process", headers=auth_headers).status_code == 403


# --- ingest -----------------------------------------------------------------

def _stub_ingest(monkeypatch, count=3):
    async def fake_ingest(session, context_id=None):
        return count

    monkeypatch.setattr(main, "ingest_intelligence", fake_ingest)
    monkeypatch.setattr(main, "_record_ingest_run", lambda *a, **kw: None)


def test_ingest_runs_when_no_cooldown(client, auth_headers, monkeypatch):
    _stub_ingest(monkeypatch)
    body = client.post("/ingest", headers=auth_headers).json()
    assert body == {"status": "success", "new_articles": 3}


def test_ingest_respects_cooldown(client, auth_headers, monkeypatch):
    _stub_ingest(monkeypatch)
    monkeypatch.setattr(
        main, "_last_ingest_at_utc", datetime.now(timezone.utc).isoformat()
    )
    body = client.post("/ingest", headers=auth_headers).json()
    assert body["status"] == "skipped"


def test_ingest_force_bypasses_cooldown(client, auth_headers, monkeypatch):
    _stub_ingest(monkeypatch)
    monkeypatch.setattr(
        main, "_last_ingest_at_utc", datetime.now(timezone.utc).isoformat()
    )
    body = client.post("/ingest", params={"force": True}, headers=auth_headers).json()
    assert body["status"] == "success"


def test_ingest_rate_limited(client, auth_headers, monkeypatch):
    _stub_ingest(monkeypatch)
    for _ in range(5):
        assert client.post("/ingest", headers=auth_headers).status_code == 200
    assert client.post("/ingest", headers=auth_headers).status_code == 429


def test_analyze_reports_already_running(client, auth_headers, monkeypatch):
    monkeypatch.setitem(main._processing, "running", True)
    assert client.post("/analyze", headers=auth_headers).json()["status"] == "already_running"
    assert client.post("/retry-insights", headers=auth_headers).json()["status"] == "already_running"
