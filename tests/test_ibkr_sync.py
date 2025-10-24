"""
Unit tests for IBKR sync functions
Tests data synchronization from IBKR to database.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from backend.services.ibkr_sync import (
    upsert_portfolio,
    upsert_account_summary,
    upsert_trades,
    sync_broker_data
)
from backend.models.portfolio import Portfolio
from backend.models.trade import Trade
from backend.models.account_summary import AccountSummary


@pytest.fixture
def mock_db():
    """Create mock database session."""
    db = Mock()
    db.query = Mock()
    db.add = Mock()
    db.commit = Mock()
    db.rollback = Mock()
    db.close = Mock()
    return db


def test_upsert_portfolio_deletes_old_and_inserts_new(mock_db):
    """Test that upsert_portfolio deletes existing and inserts new positions."""
    positions = [
        {"symbol": "AAPL", "quantity": 100, "avg_cost": 150.0},
        {"symbol": "GOOGL", "quantity": 50, "avg_cost": 2800.0}
    ]

    mock_db.query.return_value.filter_by.return_value.delete.return_value = 2

    upsert_portfolio(mock_db, user_id=1, broker_account_id=1, positions=positions)

    # Should delete old positions
    mock_db.query.assert_called_with(Portfolio)
    mock_db.query.return_value.filter_by.assert_called_with(user_id=1, broker_account_id=1)
    mock_db.query.return_value.filter_by.return_value.delete.assert_called_once()

    # Should add new positions
    assert mock_db.add.call_count == 2
    mock_db.commit.assert_called_once()


def test_upsert_account_summary(mock_db):
    """Test that upsert_account_summary updates account summary."""
    summary = {
        "total_cash": 50000.0,
        "net_liquidation": 75000.0,
        "equity_with_loan": 75000.0,
        "buying_power": 100000.0
    }

    upsert_account_summary(mock_db, user_id=1, broker_account_id=1, summary=summary)

    # Should delete old summary
    mock_db.query.assert_called_with(AccountSummary)
    mock_db.query.return_value.filter_by.return_value.delete.assert_called_once()

    # Should add new summary
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_upsert_trades_skips_duplicates(mock_db):
    """Test that upsert_trades doesn't insert duplicate exec_ids."""
    # Mock existing trades
    existing_trade = Mock()
    existing_trade.exec_id = "00001234.123456.01"
    mock_db.query.return_value.filter_by.return_value = [existing_trade]

    trades = [
        {"exec_id": "00001234.123456.01", "symbol": "AAPL", "side": "BUY", "qty": 100, "price": 150.0},
        {"exec_id": "00001235.123456.01", "symbol": "GOOGL", "side": "BUY", "qty": 50, "price": 2800.0}
    ]

    upsert_trades(mock_db, user_id=1, broker_account_id=1, trades=trades)

    # Should only add the new trade (not the duplicate)
    assert mock_db.add.call_count == 1
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_sync_broker_data_success():
    """Test successful sync of broker data."""
    mock_db = Mock()
    mock_broker_account = Mock()
    mock_broker_account.id = 1
    mock_broker_account.updated_at = datetime.utcnow()

    # Mock DB query
    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_broker_account

    # Mock IB connection
    mock_ib = Mock()
    mock_position = Mock()
    mock_position.contract.symbol = "AAPL"
    mock_position.position = 100
    mock_position.avgCost = 150.0

    mock_summary_item = Mock()
    mock_summary_item.tag = "TotalCashValue"
    mock_summary_item.value = "50000.0"

    mock_execution = Mock()
    mock_execution.execution.execId = "00001234.123456.01"
    mock_execution.execution.orderId = 1
    mock_execution.execution.side = "BUY"
    mock_execution.execution.shares = 100
    mock_execution.execution.price = 150.0
    mock_execution.execution.time = "20250101  09:30:00"
    mock_execution.contract.symbol = "AAPL"
    mock_execution.commissionReport = None

    mock_ib.reqPositionsAsync = AsyncMock(return_value=[mock_position])
    mock_ib.reqAccountSummaryAsync = AsyncMock(return_value=[mock_summary_item])
    mock_ib.reqExecutionsAsync = AsyncMock(return_value=[mock_execution])

    with patch("backend.services.ibkr_sync.SessionLocal", return_value=mock_db):
        with patch("backend.services.ibkr_sync.connection_manager.get_or_create_connection", return_value=mock_ib):
            with patch("backend.services.ibkr_sync.upsert_portfolio") as mock_upsert_portfolio:
                with patch("backend.services.ibkr_sync.upsert_account_summary") as mock_upsert_summary:
                    with patch("backend.services.ibkr_sync.upsert_trades") as mock_upsert_trades:
                        await sync_broker_data(broker_account_id=1, user_id=1)

                        # Verify functions were called
                        mock_upsert_portfolio.assert_called_once()
                        mock_upsert_summary.assert_called_once()
                        mock_upsert_trades.assert_called_once()
                        mock_db.commit.assert_called()
                        mock_db.close.assert_called_once()


@pytest.mark.asyncio
async def test_sync_broker_data_broker_account_not_found():
    """Test sync when broker account doesn't exist."""
    mock_db = Mock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    with patch("backend.services.ibkr_sync.SessionLocal", return_value=mock_db):
        await sync_broker_data(broker_account_id=999, user_id=1)

        # Should return early without doing anything
        mock_db.commit.assert_not_called()
        mock_db.close.assert_called_once()


@pytest.mark.asyncio
async def test_sync_broker_data_handles_exceptions():
    """Test that sync handles exceptions gracefully."""
    mock_db = Mock()
    mock_broker_account = Mock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_broker_account

    # Mock connection to raise exception
    with patch("backend.services.ibkr_sync.SessionLocal", return_value=mock_db):
        with patch("backend.services.ibkr_sync.connection_manager.get_or_create_connection", side_effect=Exception("Connection failed")):
            await sync_broker_data(broker_account_id=1, user_id=1)

            # Should rollback on error
            mock_db.rollback.assert_called_once()
            mock_db.close.assert_called_once()
