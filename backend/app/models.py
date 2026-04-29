# backend/app/models.py
from datetime import datetime, date
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column
from pgvector.sqlalchemy import Vector

class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    url: str = Field(unique=True)
    source: str
    published_date: datetime
    content_snippet: Optional[str] = None
    full_content: Optional[str] = None
    insight: Optional[str] = None
    category: str = Field(default="General")
    is_processed: bool = Field(default=False)

    views: int = Field(default=0)
    likes: int = Field(default=0)
    engagement_score: float = Field(default=0.0)
    last_viewed: Optional[datetime] = None
    embedding: Optional[list[float]] = Field(default=None, sa_column=Column(Vector(384)), exclude=True)
    
class Digest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow) # type: ignore
    content: str
    
class Trend(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    keyword: str = Field(index=True)
    count: int
    trend_date: date = Field(default_factory=date.today) # type: ignore # Group by day

class SavedArticle(SQLModel, table=True):
    user_id: str = Field(primary_key=True, index=True)
    article_id: int = Field(primary_key=True, index=True)
    saved_at: datetime = Field(default_factory=datetime.utcnow) # type: ignore

class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow) # type: ignore

