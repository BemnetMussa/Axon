"""Saves, views, feedback — and the per-user rate limit on feedback."""
from tests.conftest import make_article


def test_save_toggle_roundtrip(client, auth_headers, session):
    article = make_article(session)

    res = client.post(f"/articles/{article.id}/save", headers=auth_headers)
    assert res.json()["status"] == "saved"

    saved = client.get("/saved", headers=auth_headers).json()["articles"]
    assert [a["id"] for a in saved] == [article.id]

    res = client.post(f"/articles/{article.id}/save", headers=auth_headers)
    assert res.json()["status"] == "removed"

    assert client.get("/saved", headers=auth_headers).json()["articles"] == []


def test_saved_is_per_user(client, auth_headers, session):
    article = make_article(session)
    client.post(f"/articles/{article.id}/save", headers=auth_headers)

    other = {**auth_headers, "X-Axon-User-Id": "someone-else"}
    assert client.get("/saved", headers=other).json()["articles"] == []


def test_view_tracking_increments(client, auth_headers, session):
    article = make_article(session)

    for _ in range(3):
        res = client.post(f"/articles/{article.id}/view", headers=auth_headers)
        assert res.status_code == 200

    session.expire_all()
    refreshed = session.get(type(article), article.id)
    assert refreshed.views == 3
    assert refreshed.last_viewed is not None


def test_feedback_accepts_valid_rating(client, auth_headers):
    res = client.post(
        "/feedback", json={"rating": 5, "comment": "great"}, headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_feedback_rejects_out_of_range_rating(client, auth_headers):
    res = client.post("/feedback", json={"rating": 0}, headers=auth_headers)
    assert res.status_code == 422
    res = client.post("/feedback", json={"rating": 6}, headers=auth_headers)
    assert res.status_code == 422


def test_feedback_rate_limited_per_user(client, auth_headers):
    for _ in range(5):
        assert (
            client.post("/feedback", json={"rating": 4}, headers=auth_headers).status_code
            == 200
        )
    res = client.post("/feedback", json={"rating": 4}, headers=auth_headers)
    assert res.status_code == 429
    assert res.headers.get("Retry-After") == "60"

    # A different user is keyed separately and is not throttled.
    other = {**auth_headers, "X-Axon-User-Id": "user-2"}
    assert client.post("/feedback", json={"rating": 4}, headers=other).status_code == 200
