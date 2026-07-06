"""Public endpoints and the internal-secret middleware."""


def test_root_is_public(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "Axon is online"


def test_health_is_public_and_reports_db(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] in ("ok", "degraded")
    assert "db" in body and "ok" in body["db"]
    assert "scheduler" in body
    assert "last_scheduled_ingest" in body


def test_health_accepts_head(client):
    assert client.head("/health").status_code == 200


def test_docs_are_public(client):
    assert client.get("/docs").status_code == 200


def test_protected_route_rejects_missing_secret(client):
    res = client.get("/articles")
    assert res.status_code == 401


def test_protected_route_rejects_wrong_secret(client):
    res = client.get(
        "/articles",
        headers={"X-Axon-Internal-Secret": "wrong", "X-Axon-User-Id": "user-1"},
    )
    assert res.status_code == 401


def test_protected_route_rejects_missing_user_id(client):
    res = client.get("/articles", headers={"X-Axon-Internal-Secret": "test-secret"})
    assert res.status_code == 401


def test_protected_route_accepts_valid_headers(client, auth_headers):
    res = client.get("/articles", headers=auth_headers)
    assert res.status_code == 200
