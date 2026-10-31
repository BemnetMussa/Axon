"""Stored score moves up when a kept link gains points, and the freshness half stays put."""
from datetime import datetime, timezone

from app.models import Article
from engine.fetcher import _raise_kept_score


def _article(**kwargs) -> Article:
    base = dict(
        title="Kept",
        url="https://example.com/kept",
        source="HackerNews",
        published_date=datetime.now(timezone.utc),
        likes=20,
        engagement_score=0.5,
        score_recency=0.9,
    )
    base.update(kwargs)
    return Article(**base)


def test_more_points_raise_the_score_without_aging_it():
    article = _article()
    changed = _raise_kept_score(article, {"likes": 80, "norm_eng": 1.0, "recency": 0.1})
    assert changed is True
    assert article.likes == 80
    assert article.score_recency == 0.9
    assert article.engagement_score == round(1.3 * (0.55 * 1.0 + 0.45 * 0.9), 5)


def test_a_weaker_new_rank_does_not_lower_the_stored_score():
    article = _article(engagement_score=1.4, score_recency=0.95, likes=10)
    changed = _raise_kept_score(article, {"likes": 11, "norm_eng": 0.2, "recency": 0.01})
    assert changed is True
    assert article.likes == 11
    assert article.engagement_score == 1.4
    assert article.score_recency == 0.95


def test_same_point_count_leaves_the_row_alone():
    article = _article()
    assert _raise_kept_score(article, {"likes": 20, "norm_eng": 1.0, "recency": 0.1}) is False
    assert article.engagement_score == 0.5
    assert article.likes == 20


def test_a_legacy_row_locks_freshness_on_the_first_bump():
    article = _article(score_recency=None, likes=5, engagement_score=0.4)
    changed = _raise_kept_score(article, {"likes": 40, "norm_eng": 1.0, "recency": 0.3})
    assert changed is True
    assert article.score_recency == 0.3
    assert article.likes == 40
    assert article.engagement_score == round(1.3 * (0.55 * 1.0 + 0.45 * 0.3), 5)
