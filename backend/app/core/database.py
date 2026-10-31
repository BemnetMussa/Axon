import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.engine import URL
from typing import Generator
from dotenv import load_dotenv

load_dotenv(override=True)


def _build_engine():
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    if db_user and db_host:
        url = URL.create(
            drivername="postgresql+psycopg2",
            username=db_user,
            password=db_password,
            host=db_host,
            port=int(db_port or 5432),
            database=db_name or "postgres",
        )
        connect_args = {"sslmode": "require"}
    else:
        url = os.getenv(
            "DATABASE_URL",
            "postgresql://axon:axon123@127.0.0.1:5432/axon_db"
        )
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
            
        is_local = "127.0.0.1" in url or "localhost" in url
        connect_args = {"sslmode": "require"} if not is_local else {}

    return create_engine(
        url,
        echo=os.getenv("DB_ECHO", "false").lower() == "true",
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_recycle=300,
        # Supabase's session pooler caps total clients (15 on free tier), shared
        # across this app, better-auth, and any leftover connections. Keep our
        # footprint small and bounded so we can't exhaust it. Tune via env.
        pool_size=int(os.getenv("DB_POOL_SIZE", "3")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "2")),
        pool_timeout=30,
    )


engine = _build_engine()


from sqlalchemy import text

def init_db():
    try:
        with engine.connect() as conn:
            print("AXON: Testing database connection...")
            conn.execute(text("SELECT 1"))
            print("AXON: Database connection successful!")
            
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
                print("AXON: Vector extension checked/created.")
            except Exception as e:
                print(f"AXON: Failed to create vector extension (may already exist or insufficient permissions): {e}")

        SQLModel.metadata.create_all(engine)

        # create_all skips tables that already exist, so indexes added to the
        # models after first deploy never reach production. Backfill them here
        # (names match SQLModel's Field(index=True) convention: ix_<table>_<col>).
        _INDEX_BACKFILL = [
            "CREATE INDEX IF NOT EXISTS ix_article_category ON article (category)",
            "CREATE INDEX IF NOT EXISTS ix_article_source ON article (source)",
            "CREATE INDEX IF NOT EXISTS ix_article_pubdate_id ON article (published_date, id)",
            "CREATE INDEX IF NOT EXISTS ix_trend_trend_date ON trend (trend_date)",
        ]
        # create_all will not add columns to an existing article table.
        _COLUMN_BACKFILL = [
            "ALTER TABLE article ADD COLUMN IF NOT EXISTS score_recency FLOAT",
        ]
        with engine.connect() as conn:
            for ddl in _COLUMN_BACKFILL + _INDEX_BACKFILL:
                try:
                    conn.execute(text(ddl))
                    conn.commit()
                except Exception as e:
                    print(f"AXON: schema backfill skipped ({ddl.split(' ON ')[0]}): {e}")

        print("AXON: Database schema synchronized successfully!")
    except Exception as e:
        print(f"AXON: CRITICAL DATABASE INIT ERROR: {e}")
        # We don't reraise here so the app can at least start and show the ping/debug endpoints


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def get_script_session() -> Session:
    return Session(engine)
