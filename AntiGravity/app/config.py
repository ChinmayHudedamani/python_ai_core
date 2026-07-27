# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Config - Pydantic Settings

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "APEX AI Dental Assistant"
    ENVIRONMENT: str = "development"
    
    # PostgreSQL Configuration
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "apex_ai_db")
    
    # Async PostgreSQL URL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    # SQLite Knowledge Base Configuration
    SQLITE_KB_URL: str = os.getenv("SQLITE_KB_URL", "sqlite:///clinic_kb.db")

    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_URL: str = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

    # Session TTL (45 Minutes = 2700 Seconds)
    SESSION_TTL_SECONDS: int = 2700

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
