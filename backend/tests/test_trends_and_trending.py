"""Trend velocity labels and the hot-ranked trending feed (incl. its cache)."""
from datetime import date, timedelta

from app.models import Trend
from tests.conftest import make_article


def seed_trend(session, keyword: str, count: int, days_ago: int = 0):
    session.add(Trend(keyword=keyword, count=count, trend_date=date.today() - timedelta(days=days_ago)))
    session.commit()


def test_trends_empty(client, auth_headers):
    assert client.get("/trends", headers=auth_headers).json() == []


def test_trend_velocity_labels(client, auth_headers, session):
    seed_trend(session, "brand-new", 5)
    seed_trend(session, "surging", 10)
    seed_trend(session, "surging", 4, days_ago=1)
    seed_trend(session, "rising", 6)
    seed_trend(session, "rising", 5, days_ago=1)
    seed_trend(session, "steady", 3)
    seed_trend(session, "steady", 3, days_ago=1)

    by_kw = {t["keyword"]: t for t in client.get("/trends", headers=auth_headers).json()}
    assert by_kw["brand-new"]["velocity"] == "New" and by_kw["brand-new"]["is_new"]
    assert by_kw["surging"]["velocity"] == "Surging"
    assert by_kw["rising"]["velocity"] == "Rising"
    assert by_kw["steady"]["velocity"] == "Steady"


def test_trending_hot_ranking(client, auth_headers, session):
    make_article(session, title="viral-today", views=500, days_ago=0)
    make_article(session, title="old-viral", views=500, days_ago=6)
    make_article(session, title="no-views", views=0, days_ago=0)
    make_article(session, title="too-old", views=9999, days_ago=8)  # outside 7d window

    titles = [
        a["title"] for a in client.get("/articles/trending", headers=auth_headers).json()["articles"]
    ]
    assert "too-old" not in titles
    assert titles.index("viral-today") < titles.index("old-viral")
    assert titles.index("old-viral") < titles.index("no-views")


def test_trending_is_cached(client, auth_headers, session):
    make_article(session, title="first", views=10)
    first = client.get("/articles/trending", headers=auth_headers).json()["articles"]
    assert [a["title"] for a in first] == ["first"]

    # New article within the TTL window is intentionally not visible yet.
    make_article(session, title="second", views=1000)
    cached = client.get("/articles/trending", headers=auth_headers).json()["articles"]
    assert [a["title"] for a in cached] == ["first"]
