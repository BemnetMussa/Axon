"""Feed ordering, keyset pagination, filters, and payload shape."""
from tests.conftest import make_article


def get_feed(client, auth_headers, **params):
    res = client.get("/articles", params=params, headers=auth_headers)
    assert res.status_code == 200
    return res.json()


def test_empty_feed(client, auth_headers):
    body = get_feed(client, auth_headers)
    assert body["articles"] == []
    assert body["next_cursor"] is None
    assert body["has_more"] is False


def test_authority_orders_within_a_day(client, auth_headers, session):
    make_article(session, title="news", source="TechCrunch")
    make_article(session, title="community", source="HackerNews")
    make_article(session, title="lab", source="OpenAI")

    titles = [a["title"] for a in get_feed(client, auth_headers)["articles"]]
    assert titles == ["lab", "community", "news"]


def test_newer_day_beats_higher_authority(client, auth_headers, session):
    make_article(session, title="old-lab", source="OpenAI", days_ago=2)
    make_article(session, title="fresh-news", source="TechCrunch", days_ago=0)

    titles = [a["title"] for a in get_feed(client, auth_headers)["articles"]]
    assert titles == ["fresh-news", "old-lab"]


def test_cursor_pagination_no_skips_no_duplicates(client, auth_headers, session):
    sources = ["OpenAI", "HackerNews", "TechCrunch", "ArXiv", "GitHub"]
    for i in range(25):
        make_article(session, title=f"a{i}", source=sources[i % 5], days_ago=i % 4)

    full = [a["id"] for a in get_feed(client, auth_headers, limit=100)["articles"]]
    assert len(full) == 25

    paged: list[int] = []
    cursor = None
    while True:
        params = {"limit": 10}
        if cursor:
            params["cursor"] = cursor
        body = get_feed(client, auth_headers, **params)
        paged.extend(a["id"] for a in body["articles"])
        if not body["has_more"]:
            break
        cursor = body["next_cursor"]

    assert paged == full
    assert len(set(paged)) == len(paged)


def test_category_filter_scopes_feed_and_cursor(client, auth_headers, session):
    for i in range(12):
        make_article(session, title=f"ai{i}", category="AI")
    for i in range(3):
        make_article(session, title=f"sig{i}", category="Signal")

    page1 = get_feed(client, auth_headers, limit=10, category="AI")
    assert all(a["category"] == "AI" for a in page1["articles"])
    assert page1["has_more"] is True

    page2 = get_feed(client, auth_headers, limit=10, category="AI", cursor=page1["next_cursor"])
    assert all(a["category"] == "AI" for a in page2["articles"])
    assert len(page1["articles"]) + len(page2["articles"]) == 12


def test_source_filter(client, auth_headers, session):
    make_article(session, source="GitHub")
    make_article(session, source="OpenAI")

    body = get_feed(client, auth_headers, source="GitHub")
    assert [a["source"] for a in body["articles"]] == ["GitHub"]


def test_malformed_cursor_serves_from_top(client, auth_headers, session):
    make_article(session, title="only")
    body = get_feed(client, auth_headers, cursor="not-a-cursor!!")
    assert [a["title"] for a in body["articles"]] == ["only"]


def test_limit_is_capped_at_100(client, auth_headers):
    res = client.get("/articles", params={"limit": 101}, headers=auth_headers)
    assert res.status_code == 422


def test_feed_payload_excludes_full_content_and_embedding(client, auth_headers, session):
    make_article(session, full_content="x" * 8000)
    article = get_feed(client, auth_headers)["articles"][0]
    assert "full_content" not in article
    assert "embedding" not in article
    # Fields the frontend renders must survive the slimming.
    for key in ("id", "title", "url", "source", "category", "published_date", "views", "likes"):
        assert key in article


def test_count_since(client, auth_headers, session):
    first = make_article(session)
    make_article(session)
    make_article(session)

    res = client.get(
        "/articles/count-since", params={"since_id": first.id}, headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json()["new_count"] == 2
