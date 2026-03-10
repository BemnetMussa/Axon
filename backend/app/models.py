# backend/app/models.py
from datetime import datetime, date
from typing import Optional
from sqlmodel import Field, SQLModel

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
    
    
class Trend(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    keyword: str = Field(index=True)
    count: int
    trend_date: date = Field(default_factory=date.today) # type: ignore # Group by day

