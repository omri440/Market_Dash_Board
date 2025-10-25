"""
Pytest configuration and shared fixtures.
This file is automatically loaded by pytest.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


@pytest.fixture
def mock_db_session():
    """
    Create a mock database session for testing.
    Returns a Mock object that simulates SQLAlchemy session.
    """
    db = Mock()
    db.query = Mock()
    db.add = Mock()
    db.commit = Mock()
    db.rollback = Mock()
    db.close = Mock()
    db.refresh = Mock()
    return db


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": 1,
        "username": "testuser",
        "password_hash": "$2b$12$somehash",
        "role": "user"
    }


@pytest.fixture
def sample_broker_account_data():
    """Sample broker account data for testing."""
    return {
        "id": 1,
        "user_id": 1,
        "broker": "ibkr",
        "account_code": "U1234567",
        "conn_host": "127.0.0.1",
        "conn_port": 7497,
        "client_id": 1,
        "status": "active",
        "label": "Test Account"
    }


@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio position data."""
    return [
        {
            "symbol": "AAPL",
            "quantity": 100.0,
            "avg_cost": 150.0,
            "current_price": 160.0,
            "market_value": 16000.0,
            "unrealized_pnl": 1000.0,
            "realized_pnl": 0.0
        },
        {
            "symbol": "GOOGL",
            "quantity": 50.0,
            "avg_cost": 2800.0,
            "current_price": 2900.0,
            "market_value": 145000.0,
            "unrealized_pnl": 5000.0,
            "realized_pnl": 0.0
        }
    ]


@pytest.fixture
def sample_account_summary_data():
    """Sample account summary data."""
    return {
        "total_cash": 50000.0,
        "net_liquidation": 211000.0,
        "equity_with_loan": 211000.0,
        "buying_power": 100000.0
    }


@pytest.fixture
def sample_trades_data():
    """Sample trade execution data."""
    return [
        {
            "exec_id": "00001234.123456.01",
            "order_id": "1001",
            "symbol": "AAPL",
            "side": "BUY",
            "qty": 100.0,
            "price": 150.0,
            "realized_pnl": None,
            "trade_time": "2025-01-01 09:30:00"
        },
        {
            "exec_id": "00001235.123456.01",
            "order_id": "1002",
            "symbol": "GOOGL",
            "side": "BUY",
            "qty": 50.0,
            "price": 2800.0,
            "realized_pnl": None,
            "trade_time": "2025-01-01 10:15:00"
        }
    ]


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """
    Clear settings cache before each test.
    This ensures tests don't interfere with each other.
    """
    from backend.config import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def mock_ib_connection():
    """
    Mock IBKR connection for testing.
    Returns a Mock IB object with common methods.
    """
    ib = Mock()
    ib.isConnected = Mock(return_value=True)
    ib.connectAsync = Mock()
    ib.disconnect = Mock()
    ib.reqPositionsAsync = Mock()
    ib.reqAccountSummaryAsync = Mock()
    ib.reqExecutionsAsync = Mock()
    return ib


# Pytest configuration
def pytest_configure(config):
    """
    Pytest configuration hook.
    Adds custom markers.
    """
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow-running tests")
    config.addinivalue_line("markers", "requires_db: Tests that require database")
    config.addinivalue_line("markers", "requires_ibkr: Tests that require IBKR connection")
