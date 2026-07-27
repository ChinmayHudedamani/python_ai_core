# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI SQLite SQLModel Engine & Session for Knowledge Base

from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# Create SQLite Synchronous Engine for read-heavy Knowledge Base
sqlite_engine = create_engine(
    settings.SQLITE_KB_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

def init_sqlite_db():
    """Initializes SQLite Knowledge Base database schema."""
    SQLModel.metadata.create_all(sqlite_engine)

def get_sqlite_session() -> Session:
    """Returns a new synchronous SQLModel session for Knowledge Base queries."""
    return Session(sqlite_engine)
