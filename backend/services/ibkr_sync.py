from sqlalchemy.orm import Session
from backend.db import Session as SessionLocal
from backend.models.broker_account import BrokerAccount
from backend.services.ibkr_connection_manager import connection_manager
from backend.services.ibkr_client import IBKRClient
import asyncio


async def sync_broker_data(broker_account_id: int, user_id: int):
    """
    Background task to sync data from IBKR.
    """
    db: Session = SessionLocal()
    try:
        broker_account = db.query(BrokerAccount).filter_by(id=broker_account_id).first()
        if not broker_account:
            return

        # Get connection
        ib = await connection_manager.get_or_create_connection(broker_account)

        # Fetch data
        positions = await ib.reqPositionsAsync()
        account_summary = await ib.reqAccountSummaryAsync()
        executions = await ib.reqExecutionsAsync()

        # Transform and upsert
        positions_data = [
            {
                "symbol": p.contract.symbol,
                "quantity": p.position,
                "avg_cost": p.avgCost,
                "current_price": None,  # Need market data subscription
                "market_value": p.position * p.avgCost,
                "unrealized_pnl": 0,
                "realized_pnl": 0
            }
            for p in positions
        ]

        # Upsert using existing functions
        from backend.services.ibkr_sync import upsert_portfolio, upsert_trades
        upsert_portfolio(db, user_id, broker_account_id, positions_data)

        # Similar for trades...

        db.commit()
    except Exception as e:
        print(f"Sync error for broker_account {broker_account_id}: {e}")
        db.rollback()
    finally:
        db.close()