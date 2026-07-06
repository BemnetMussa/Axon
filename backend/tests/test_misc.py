"""RSS output, cursor encoding, and content endpoint fallbacks."""
import pytest

import app.main as main
from tests.conftest import make_article


def test_rss_feed(client, auth_headers, session):
    make_article(session, title="Rss <Title> & stuff", insight="the insight")
    res = client.get("/rss", headers=auth_headers)
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/rss+xml")
    assert "Rss <Title> & stuff" in res.text
    assert "the insight" in res.text


@pytest.mark.parametrize("sort_key,article_id", [(0, 1), (2064060, 42), (99999999999, 1)])
def test_cursor_roundtrip(sort_key, article_id):
    cursor = main._encode_cursor(sort_key, article_id)
    assert main._decode_cursor(cursor) == (sort_key, article_id)


def test_decode_rejects_garbage():
    with pytest.raises(Exception):
        main._decode_cursor("!!!not-base64!!!")


def test_content_serves_stored_full_content(client, auth_headers, session):
    article = make_article(session, full_content="stored body")
    body = client.get(f"/articles/{article.id}/content", headers=auth_headers).json()
    assert body["content"] == "stored body"


def test_content_falls_back_to_snippet_when_extraction_fails(
    client, auth_headers, session, monkeypatch
):
    async def no_content(url):
        return None

    monkeypatch.setattr(main, "extract_article_content", no_content)
    article = make_article(session)  # content_snippet="snippet", no full_content
    body = client.get(f"/articles/{article.id}/content", headers=auth_headers).json()
    assert body["content"] == "snippet"


def test_content_persists_extracted_text(client, auth_headers, session, monkeypatch):
    async def fake_extract(url):
        return "extracted text"

    monkeypatch.setattr(main, "extract_article_content", fake_extract)
    article = make_article(session)
    body = client.get(f"/articles/{article.id}/content", headers=auth_headers).json()
    assert body["content"] == "extracted text"

    session.expire_all()
    assert session.get(type(article), article.id).full_content == "extracted text"


def test_content_unknown_article_404(client, auth_headers):
    assert client.get("/articles/9999/content", headers=auth_headers).status_code == 404
