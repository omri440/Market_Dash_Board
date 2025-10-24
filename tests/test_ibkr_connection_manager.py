"""
Unit tests for IBKR Connection Manager
Tests connection pooling and lifecycle management.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from backend.services.ibkr_connection_manager import IBKRConnectionManager
from backend.models.broker_account import BrokerAccount


@pytest.fixture
def connection_manager():
    """Create a fresh connection manager for each test."""
    return IBKRConnectionManager()


@pytest.fixture
def mock_broker_account():
    """Create a mock broker account."""
    account = Mock(spec=BrokerAccount)
    account.id = 1
    account.conn_host = "127.0.0.1"
    account.conn_port = 7497
    account.client_id = 1
    return account


@pytest.mark.asyncio
async def test_get_or_create_connection_creates_new(connection_manager, mock_broker_account):
    """Test that new connection is created when none exists."""
    with patch("backend.services.ibkr_connection_manager.IB") as MockIB:
        mock_ib = MockIB.return_value
        mock_ib.connectAsync = AsyncMock()
        mock_ib.isConnected.return_value = False

        ib = await connection_manager.get_or_create_connection(mock_broker_account)

        assert ib is not None
        mock_ib.connectAsync.assert_called_once_with("127.0.0.1", 7497, clientId=1)


@pytest.mark.asyncio
async def test_get_or_create_connection_reuses_existing(connection_manager, mock_broker_account):
    """Test that existing connection is reused."""
    with patch("backend.services.ibkr_connection_manager.IB") as MockIB:
        mock_ib = MockIB.return_value
        mock_ib.connectAsync = AsyncMock()
        mock_ib.isConnected.return_value = True

        # First call - creates connection
        ib1 = await connection_manager.get_or_create_connection(mock_broker_account)

        # Second call - should reuse
        mock_ib.isConnected.return_value = True
        ib2 = await connection_manager.get_or_create_connection(mock_broker_account)

        assert ib1 is ib2  # Same object
        assert mock_ib.connectAsync.call_count == 1  # Only connected once


@pytest.mark.asyncio
async def test_disconnect_closes_connection(connection_manager, mock_broker_account):
    """Test that disconnect closes and removes connection."""
    with patch("backend.services.ibkr_connection_manager.IB") as MockIB:
        mock_ib = MockIB.return_value
        mock_ib.connectAsync = AsyncMock()
        mock_ib.isConnected.return_value = True
        mock_ib.disconnect = Mock()

        # Create connection
        await connection_manager.get_or_create_connection(mock_broker_account)

        # Disconnect
        await connection_manager.disconnect(mock_broker_account.id)

        mock_ib.disconnect.assert_called_once()
        assert mock_broker_account.id not in connection_manager._connections


@pytest.mark.asyncio
async def test_disconnect_all_closes_all_connections(connection_manager):
    """Test that disconnect_all closes all connections."""
    with patch("backend.services.ibkr_connection_manager.IB") as MockIB:
        mock_ib = MockIB.return_value
        mock_ib.connectAsync = AsyncMock()
        mock_ib.isConnected.return_value = True
        mock_ib.disconnect = Mock()

        # Create multiple connections
        account1 = Mock(id=1, conn_host="127.0.0.1", conn_port=7497, client_id=1)
        account2 = Mock(id=2, conn_host="127.0.0.1", conn_port=7497, client_id=2)

        await connection_manager.get_or_create_connection(account1)
        await connection_manager.get_or_create_connection(account2)

        # Disconnect all
        await connection_manager.disconnect_all()

        assert len(connection_manager._connections) == 0
        assert mock_ib.disconnect.call_count >= 2


def test_get_connection_status_nonexistent(connection_manager):
    """Test connection status for non-existent connection."""
    status = connection_manager.get_connection_status(999)

    assert status["exists"] is False
    assert status["connected"] is False


@pytest.mark.asyncio
async def test_get_connection_status_exists(connection_manager, mock_broker_account):
    """Test connection status for existing connection."""
    with patch("backend.services.ibkr_connection_manager.IB") as MockIB:
        mock_ib = MockIB.return_value
        mock_ib.connectAsync = AsyncMock()
        mock_ib.isConnected.return_value = True

        await connection_manager.get_or_create_connection(mock_broker_account)

        status = connection_manager.get_connection_status(mock_broker_account.id)

        assert status["exists"] is True
        assert status["connected"] is True
