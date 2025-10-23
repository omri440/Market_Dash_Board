# backend/config.py
"""
Centralized configuration management using Pydantic Settings.
All environment variables are loaded from .env file.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Reads from .env file automatically.
    """

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # IBKR Connection Defaults
    IBKR_DEFAULT_HOST: str = "127.0.0.1"
    IBKR_DEFAULT_PORT: int = 7497
    IBKR_PAPER_PORT: int = 7497
    IBKR_LIVE_PORT: int = 7496

    # Redis (for ARQ task queue)
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance (singleton pattern).

    Usage:
        from backend.config import get_settings
        settings = get_settings()
        print(settings.DATABASE_URL)
    """
    return Settings()


# Convenience export for direct import
settings = get_settings()
