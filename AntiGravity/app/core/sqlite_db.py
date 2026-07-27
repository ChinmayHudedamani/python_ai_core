"""Synchronous SQLite engine and session management for the relational Knowledge Base."""

from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings

sqlite_file_name = settings.SQLITE_KB_PATH
sqlite_url = f"sqlite:///{sqlite_file_name}"

sqlite_engine = create_engine(
    sqlite_url,
    echo=False,
    connect_args={"check_same_thread": False}
)


def init_sqlite_db():
    """Initializes SQLite database schema for Knowledge Base tables."""
    SQLModel.metadata.create_all(sqlite_engine)


def get_sqlite_session():
    """Yields a synchronous SQLite session for Knowledge Base queries."""
    with Session(sqlite_engine) as session:
        yield session
