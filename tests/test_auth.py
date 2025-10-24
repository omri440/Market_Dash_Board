"""
Unit tests for authentication (JWT handler and auth dependency)
"""
import pytest
from datetime import datetime, timedelta
from backend.utils.jwt_handler import create_access_token, verify_access_token
from backend.utils.auth_dependency import get_current_user
from backend.models.user import User
from fastapi import HTTPException
from unittest.mock import Mock


def test_create_access_token():
    """Test JWT token creation."""
    data = {"sub": "testuser", "role": "user"}
    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_valid_token():
    """Test verifying a valid JWT token."""
    data = {"sub": "testuser", "role": "user"}
    token = create_access_token(data)

    payload = verify_access_token(token)

    assert payload is not None
    assert payload["sub"] == "testuser"
    assert payload["role"] == "user"
    assert "exp" in payload  # Has expiration


def test_verify_invalid_token():
    """Test verifying an invalid JWT token."""
    invalid_token = "invalid.token.string"

    payload = verify_access_token(invalid_token)

    assert payload is None


def test_verify_expired_token(monkeypatch):
    """Test that expired tokens are rejected."""
    # Mock timedelta to create already-expired token
    from backend.utils import jwt_handler
    original_expire = jwt_handler.ACCESS_TOKEN_EXPIRE_MINUTES

    # Set to negative value (already expired)
    monkeypatch.setattr(jwt_handler, "ACCESS_TOKEN_EXPIRE_MINUTES", -1)

    data = {"sub": "testuser"}
    token = create_access_token(data)

    # Restore original value
    monkeypatch.setattr(jwt_handler, "ACCESS_TOKEN_EXPIRE_MINUTES", original_expire)

    payload = verify_access_token(token)

    assert payload is None  # Expired token returns None


def test_get_current_user_with_valid_token(monkeypatch):
    """Test get_current_user with valid token and existing user."""
    # Create mock objects
    mock_credentials = Mock()
    mock_credentials.credentials = create_access_token({"sub": "testuser"})

    mock_db = Mock()
    mock_user = User(id=1, username="testuser", password_hash="hashed", role="user")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    # Test
    user = get_current_user(credentials=mock_credentials, db=mock_db)

    assert user == mock_user
    assert user.username == "testuser"


def test_get_current_user_with_invalid_token():
    """Test get_current_user with invalid token raises 401."""
    mock_credentials = Mock()
    mock_credentials.credentials = "invalid.token"

    mock_db = Mock()

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=mock_credentials, db=mock_db)

    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


def test_get_current_user_with_nonexistent_user():
    """Test get_current_user when user doesn't exist in DB."""
    mock_credentials = Mock()
    mock_credentials.credentials = create_access_token({"sub": "nonexistent"})

    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None  # User not found

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=mock_credentials, db=mock_db)

    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail
