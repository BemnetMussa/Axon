# Run this once to add new columns
# backend/migration.py (create this file)

from sqlmodel import create_engine, Session
from app.models import Article
from app.core.database import engine

def migrate():
    """Add new engagement fields to existing articles"""
    with Session(engine) as session:
        articles = session.query(Article).all()
        for article in articles:
            article.views = 0
            article.likes = 0
            article.engagement_score = 0.0
            session.add(article)
        session.commit()
        print(f"✅ Migrated {len(articles)} articles")

if __name__ == "__main__":
    migrate()
