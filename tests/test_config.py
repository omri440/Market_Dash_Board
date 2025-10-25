"""
Unit tests for backend/config.py
Tests centralized configuration management.
"""
import pytest
from backend.config import Settings, get_settings


def test_settings_loads_from_env(monkeypatch):
    """Test that settings load from environment variables."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/testdb")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-12345")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/1")

    # Clear cache
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.DATABASE_URL == "postgresql://test:test@localhost/testdb"
    assert settings.SECRET_KEY == "test-secret-key-12345"
    assert settings.REDIS_URL == "redis://localhost:6379/1"


def test_settings_default_values():
    """Test default values for optional settings."""
    get_settings.cache_clear()
    settings = get_settings()

    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
    assert settings.IBKR_DEFAULT_HOST == "127.0.0.1"
    assert settings.IBKR_DEFAULT_PORT == 7497


def test_settings_singleton():
    """Test that get_settings returns the same instance (cached)."""
    settings1 = get_settings()
    settings2 = get_settings()

    assert settings1 is settings2  # Same object in memory
