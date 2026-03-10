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
        connect_args = {}

    return create_engine(
        url,
        echo=os.getenv("DB_ECHO", "false").lower() == "true",
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_recycle=300,
    )


engine = _build_engine()


def init_db():
    SQLModel.metadata.create_all(engine)
    print("Database initialized successfully!")


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def get_script_session() -> Session:
    return Session(engine)
