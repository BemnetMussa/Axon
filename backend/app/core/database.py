# backend/app/core/database.py
import os
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from dotenv import load_dotenv

load_dotenv()

# 1. Configuration
# We keep your robust env var fetching. Good practice!
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://axon:axon123@127.0.0.1:5432/axon_db"
)

# 2. Engine Creation
# echo=True is great for dev, but we might want to turn it off in prod later.
engine = create_engine(DATABASE_URL, echo=True)

# 3. Initialization
def init_db():
    """
    Creates the tables. 
    NOTE: SQLModel.metadata includes all classes that inherit from SQLModel.
    We don't need a separate 'Base'.
    """
    SQLModel.metadata.create_all(engine)
    print("Database initialized successfully!")

# 4. Dependency (The FastAPI Way)
def get_session() -> Generator[Session, None, None]:
    """
    Yields a database session. 
    FastAPI uses this to inject the session into endpoints.
    """
    with Session(engine) as session:
        yield session

# 5. Direct Session (The Script Way)
def get_script_session() -> Session:
    """
    Returns a session for standalone scripts (like scrapers) 
    that aren't running inside a web request.
    """
    return Session(engine)