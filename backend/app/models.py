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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_processed: bool = Field(default=False) 

class Trend(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    keyword: str = Field(index=True)
    count: int
    trend_date: date = Field(default_factory=date.today) # type: ignore # Group by day