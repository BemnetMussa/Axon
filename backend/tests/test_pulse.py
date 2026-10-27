"""/pulse — scanned vs. kept aggregates for the landing readout and sweep panel."""
from datetime import datetime, timedelta, timezone

from app.models import IngestRun
from tests.conftest import make_article


def _run(session, *, hours_ago: float, raw: int, kept: int, ok: bool = True):
    started = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    session.add(
        IngestRun(
            started_at=started,
            finished_at=started + timedelta(minutes=2),
            ok=ok,
            raw_found=raw,
            new_articles=kept,
        )
    )
    session.commit()


def test_pulse_requires_internal_auth(client):
    assert client.get("/pulse").status_code == 401


def test_pulse_empty_database(client, auth_headers):
    body = client.get("/pulse", headers=auth_headers).json()
    assert body["last_sweep_at"] is None
    assert body["last_scanned"] == 0
    assert body["last_kept"] == 0
    assert body["scanned_24h"] == 0
    assert body["kept_24h"] == 0
    assert body["next_sweep_at"] is None


def test_pulse_aggregates_recent_successful_runs(client, session, auth_headers):
    _run(session, hours_ago=30, raw=999, kept=99)  # outside the 24h window
    _run(session, hours_ago=6, raw=150, kept=12)
    _run(session, hours_ago=3, raw=500, kept=500, ok=False)  # failed runs ignored
    _run(session, hours_ago=1, raw=140, kept=9)
    make_article(session, source="HackerNews")
    make_article(session, source="GitHub")
    make_article(session, source="GitHub")

    body = client.get("/pulse", headers=auth_headers).json()
    assert body["last_scanned"] == 140
    assert body["last_kept"] == 9
    assert body["scanned_24h"] == 290
    assert body["kept_24h"] == 21
    assert body["sweeps_24h"] == 2
    assert body["sources"] == 2
    assert body["last_sweep_at"] is not None
    assert body["next_sweep_at"] is not None
    assert body["kept_total"] == 3
    assert body["sweeps_total"] == 3
    assert body["scanned_total"] == 999 + 150 + 140
    assert body["running_since"] is not None


def test_pulse_reports_observed_cadence(client, session, auth_headers):
    for h in (40, 32, 24, 16, 8, 0.5):
        _run(session, hours_ago=h, raw=100, kept=10)

    body = client.get("/pulse", headers=auth_headers).json()
    assert body["interval_hours"] == 8
    started = datetime.now(timezone.utc) - timedelta(hours=0.5)
    nxt = datetime.fromisoformat(body["next_sweep_at"])
    assert abs((nxt - (started + timedelta(hours=8))).total_seconds()) < 120
