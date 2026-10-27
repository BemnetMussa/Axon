"""Shared fixtures for the Axon backend test suite.

The app is exercised through Starlette's TestClient against an in-memory SQLite
database (dependency-overridden), with all external services — Groq, feed
fetching, embeddings — monkeypatched. AXON_INTERNAL_SECRET must be set *before*
app.main is imported (it hard-fails without it), hence the env block up top.
"""
import os

os.environ["AXON_INTERNAL_SECRET"] = "test-secret"
os.environ.setdefault("GROQ_API_KEY", "gsk_test_dummy_key")
os.environ["DISABLE_SCHEDULER"] = "1"
os.environ["AXON_ADMIN_USER_IDS"] = "admin-user"

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine
from starlette.testclient import TestClient

import app.main as main
from app.core.database import get_session
from app.models import Article

TEST_SECRET = "test-secret"
USER_ID = "user-1"
ADMIN_ID = "admin-user"

# main.py load_dotenv(override=True) lets a developer's backend/.env clobber the
# env vars set above, so pin the already-imported module globals to test values.
main.INTERNAL_SECRET = TEST_SECRET
main.ADMIN_USER_IDS = {ADMIN_ID}


@pytest.fixture()
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def session(engine):
    with Session(engine) as s:
        yield s


@pytest.fixture(autouse=True)
def _reset_app_state(monkeypatch, engine):
    """Isolate per-test app state: rate-limit counters, in-memory caches, and
    scheduler bookkeeping globals. Stubs the Groq liveness probe and points the
    health check's engine at the test database so no test touches the network
    or a real Postgres."""
    monkeypatch.setattr(main, "INTERNAL_SECRET", TEST_SECRET)
    monkeypatch.setattr(main, "ADMIN_USER_IDS", {ADMIN_ID})
    monkeypatch.setattr(main, "EXPOSE_API_DOCS", False)
    monkeypatch.setattr(main, "db_engine", engine)
    main.limiter.reset()
    main._suggestions_cache.clear()
    main._trending_cache.clear()
    main._trends_cache.clear()
    main._digest_cache.clear()
    main._db_health_cache.clear()
    main._pulse_cache.clear()
    monkeypatch.setattr(main, "_last_ingest_at_utc", None)
    monkeypatch.setattr(
        main, "probe_groq", lambda: {"key_present": True, "reachable": True, "error": None}
    )
    monkeypatch.setitem(main._groq_probe_cache, "value", None)
    monkeypatch.setitem(main._groq_probe_cache, "at", 0.0)
    yield
    main.app.dependency_overrides.clear()


@pytest.fixture()
def client(engine):
    def override_get_session():
        with Session(engine) as s:
            yield s

    main.app.dependency_overrides[get_session] = override_get_session
    # No context manager on purpose: lifespan (init_db + scheduler) must not run.
    return TestClient(main.app)


@pytest.fixture()
def auth_headers():
    return {"X-Axon-Internal-Secret": TEST_SECRET, "X-Axon-User-Id": USER_ID}


@pytest.fixture()
def admin_headers():
    return {"X-Axon-Internal-Secret": TEST_SECRET, "X-Axon-User-Id": ADMIN_ID}


_url_counter = 0


def make_article(
    session: Session,
    *,
    title: str = "Test article",
    source: str = "HackerNews",
    category: str = "AI",
    days_ago: float = 0,
    views: int = 0,
    likes: int = 0,
    score: float = 0.0,
    insight: str | None = None,
    full_content: str | None = None,
    is_processed: bool = False,
) -> Article:
    global _url_counter
    _url_counter += 1
    article = Article(
        title=title,
        url=f"https://example.com/a/{_url_counter}",
        source=source,
        category=category,
        published_date=datetime.now(timezone.utc) - timedelta(days=days_ago),
        views=views,
        likes=likes,
        engagement_score=score,
        insight=insight,
        full_content=full_content,
        is_processed=is_processed,
        content_snippet="snippet",
    )
    session.add(article)
    session.commit()
    session.refresh(article)
    return article
