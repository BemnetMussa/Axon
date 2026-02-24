# backend/migration.py
from sqlalchemy import text
from sqlmodel import Session
from app.models import Article
from app.core.database import engine

def migrate():
    """Add new engagement fields to existing articles and update data"""
    print("🚀 Starting migration...")
    
    with engine.connect() as conn:
        # Add columns if they don't exist (PostgreSQL syntax)
        columns_to_add = [
            ("views", "INTEGER DEFAULT 0"),
            ("likes", "INTEGER DEFAULT 0"),
            ("engagement_score", "FLOAT DEFAULT 0.0"),
            ("last_viewed", "TIMESTAMP")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE article ADD COLUMN {col_name} {col_type}"))
                print(f"✅ Added column: {col_name}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"ℹ️ Column '{col_name}' already exists, skipping.")
                else:
                    print(f"⚠️ Error adding column {col_name}: {e}")
        conn.commit()

    # Now update existing records using Session
    with Session(engine) as session:
        articles = session.query(Article).all()
        count = 0
        for article in articles:
            if article.views is None: article.views = 0
            if article.likes is None: article.likes = 0
            if article.engagement_score is None: article.engagement_score = 0.0
            session.add(article)
            count += 1
        
        session.commit()
        print(f"✨ Successfully initialized data for {count} articles.")

if __name__ == "__main__":
    migrate()
