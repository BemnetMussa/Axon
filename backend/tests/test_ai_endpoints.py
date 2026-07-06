"""Chat, suggestions, briefs, digests — Groq is always monkeypatched."""
import app.main as main
from tests.conftest import make_article


def test_chat_unknown_article_404(client, auth_headers):
    res = client.post("/articles/9999/chat", json={"question": "hi"}, headers=auth_headers)
    assert res.status_code == 404


def test_chat_validates_question_bounds(client, auth_headers, session):
    article = make_article(session)
    res = client.post(f"/articles/{article.id}/chat", json={"question": ""}, headers=auth_headers)
    assert res.status_code == 422
    res = client.post(
        f"/articles/{article.id}/chat", json={"question": "x" * 1001}, headers=auth_headers
    )
    assert res.status_code == 422


def test_chat_answers(client, auth_headers, session, monkeypatch):
    monkeypatch.setattr(main, "chat_about_article", lambda **kw: f"echo: {kw['question']}")
    article = make_article(session)
    res = client.post(
        f"/articles/{article.id}/chat", json={"question": "why?"}, headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json()["answer"] == "echo: why?"


def test_suggestions_cached_after_first_call(client, auth_headers, session, monkeypatch):
    calls = {"n": 0}

    def fake_suggestions(**kw):
        calls["n"] += 1
        return ["q1", "q2", "q3"]

    monkeypatch.setattr(main, "generate_chat_suggestions", fake_suggestions)
    article = make_article(session)

    first = client.get(f"/articles/{article.id}/suggestions", headers=auth_headers).json()
    assert first == {"suggestions": ["q1", "q2", "q3"], "cached": False}

    second = client.get(f"/articles/{article.id}/suggestions", headers=auth_headers).json()
    assert second == {"suggestions": ["q1", "q2", "q3"], "cached": True}
    assert calls["n"] == 1


def test_suggestions_cache_is_bounded(monkeypatch):
    monkeypatch.setattr(main, "_SUGGESTIONS_MAX", 3)
    for i in range(10):
        main._set_cached_suggestions(i, [f"s{i}"])
    assert len(main._suggestions_cache) <= 3
    # Most recent entry survives eviction.
    assert main._get_cached_suggestions(9) == ["s9"]


def test_brief_unknown_article_404(client, auth_headers):
    assert client.get("/brief/9999", headers=auth_headers).status_code == 404


def test_brief_returns_generated_content(client, auth_headers, session, monkeypatch):
    monkeypatch.setattr(main, "generate_deep_brief", lambda title, content: "the brief")
    article = make_article(session, title="Big paper")
    body = client.get(f"/brief/{article.id}", headers=auth_headers).json()
    assert body == {"title": "Big paper", "brief": "the brief"}


def test_digest_latest_empty(client, auth_headers):
    body = client.get("/digests/latest", headers=auth_headers).json()
    assert "No weekly digest" in body["content"]


def test_digest_generate_and_read_back(client, auth_headers, session, monkeypatch):
    monkeypatch.setattr(main, "generate_weekly_digest", lambda s: "fresh digest")
    res = client.post("/digests/generate", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["digest"] == "fresh digest"


def test_digest_generate_without_articles_503(client, auth_headers, monkeypatch):
    monkeypatch.setattr(main, "generate_weekly_digest", lambda s: None)
    res = client.post("/digests/generate", headers=auth_headers)
    assert res.status_code == 503


def test_semantic_search_validates_query(client, auth_headers):
    assert client.get("/search/semantic", headers=auth_headers).status_code == 422
    res = client.get("/search/semantic", params={"query": "x" * 201}, headers=auth_headers)
    assert res.status_code == 422
