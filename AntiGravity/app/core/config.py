"""Application environment configuration settings using Pydantic Settings."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "APEX AI Dental Assistant"
    ENVIRONMENT: str = "production"

    POSTGRES_USER: str = "apex_user"
    POSTGRES_PASSWORD: str = "apex_secure_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "apex_dental_db"
    DATABASE_URL: str = ""

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    SQLITE_KB_PATH: str = "clinic_kb.db"

    WHATSAPP_PHONE_NUMBER_ID: str = "default_phone_id"
    WHATSAPP_ACCESS_TOKEN: str = "default_access_token"
    WHATSAPP_VERIFY_TOKEN: str = "apex_ai_secure_verify_token_2026"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def __init__(self, **values):
        super().__init__(**values)
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )


settings = Settings()
