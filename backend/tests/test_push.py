"""Per-story push selection: weekly score bar, per-sweep and daily caps."""
from datetime import datetime, timedelta, timezone

import app.main as main
from tests.conftest import make_article


def _week_of_scores(session, n=10):
    return [make_article(session, title=f"old {i}", score=i / 10, days_ago=2) for i in range(n)]


def test_picks_at_most_two_strong_new_stories(session):
    old = _week_of_scores(session)
    since = old[-1].id
    weak = make_article(session, title="weak", score=0.1)
    a = make_article(session, title="a", score=1.5)
    b = make_article(session, title="b", score=1.4)
    make_article(session, title="c", score=1.3)

    picked = main._pick_push_stories(session, since)

    assert [s.id for s in picked] == [a.id, b.id]
    assert weak.id not in [s.id for s in picked]


def test_nothing_clears_the_bar_means_no_push(session):
    old = _week_of_scores(session)
    make_article(session, title="meh", score=0.2)

    assert main._pick_push_stories(session, old[-1].id) == []


def test_daily_cap_stops_pushes(session):
    old = _week_of_scores(session)
    since = old[-1].id
    now = datetime.now(timezone.utc)
    for i in range(main.PUSH_MAX_PER_DAY - 1):
        sent = make_article(session, title=f"sent {i}", score=0.0)
        sent.notified_at = now
        session.add(sent)
    session.commit()
    since = max(since, sent.id)
    make_article(session, title="x", score=1.5)
    make_article(session, title="y", score=1.4)

    assert len(main._pick_push_stories(session, since, now=now)) == 1


def test_already_notified_story_is_not_pushed_again(session):
    old = _week_of_scores(session)
    story = make_article(session, title="once", score=1.5)
    story.notified_at = datetime.now(timezone.utc) - timedelta(days=1)
    session.add(story)
    session.commit()

    assert main._pick_push_stories(session, old[-1].id) == []


def test_read_single_article(client, auth_headers, session):
    article = make_article(session, title="deep link", full_content="body")

    body = client.get(f"/articles/{article.id}", headers=auth_headers).json()

    assert body["id"] == article.id
    assert body["title"] == "deep link"
    assert "full_content" not in body
    assert "notified_at" not in body


def test_read_single_article_404(client, auth_headers):
    assert client.get("/articles/999999", headers=auth_headers).status_code == 404


def test_count_since_still_routes(client, auth_headers):
    assert client.get("/articles/count-since?since_id=0", headers=auth_headers).status_code == 200
