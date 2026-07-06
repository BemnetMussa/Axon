# backend/app/models.py
from datetime import datetime, date, timezone
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Index
from pgvector.sqlalchemy import Vector


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

class Article(SQLModel, table=True):
    # Compound index backs keyset pagination ordered by (published_date, id).
    # Ascending btree; Postgres scans it backward for the DESC feed order.
    __table_args__ = (Index("ix_article_pubdate_id", "published_date", "id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    url: str = Field(unique=True)
    source: str = Field(index=True)
    published_date: datetime
    content_snippet: Optional[str] = None
    full_content: Optional[str] = None
    insight: Optional[str] = None
    category: str = Field(default="General", index=True)
    is_processed: bool = Field(default=False)

    views: int = Field(default=0)
    likes: int = Field(default=0)
    engagement_score: float = Field(default=0.0)
    last_viewed: Optional[datetime] = None
    embedding: Optional[list[float]] = Field(default=None, sa_column=Column(Vector(384)), exclude=True)
    
class Digest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utcnow)
    content: str
    
class Trend(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    keyword: str = Field(index=True)
    count: int
    trend_date: date = Field(default_factory=date.today, index=True) # type: ignore # Group by day

class SavedArticle(SQLModel, table=True):
    user_id: str = Field(primary_key=True, index=True)
    article_id: int = Field(primary_key=True, index=True)
    saved_at: datetime = Field(default_factory=_utcnow)

class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)

class IngestRun(SQLModel, table=True):
    """One row per real ingestion run, so the admin dashboard's history survives
    process restarts (in-memory counters reset on every Render redeploy/sleep)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    started_at: datetime = Field(default_factory=_utcnow, index=True)
    finished_at: Optional[datetime] = None
    trigger: str = Field(default="scheduler")  # scheduler | manual | cron
    ok: bool = Field(default=True)
    new_articles: int = Field(default=0)
    analyzed: int = Field(default=0)
    raw_found: int = Field(default=0)
    sources_json: Optional[str] = None  # JSON {source: {raw, ingested}}
    detail: Optional[str] = None

