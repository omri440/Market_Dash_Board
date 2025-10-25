from sqlalchemy.orm import Session
from backend.db import Session as SessionLocal
from backend.models.broker_account import BrokerAccount
from backend.models.portfolio import Portfolio
from backend.models.trade import Trade
from backend.models.account_summary import AccountSummary
from backend.services.ibkr_connection_manager import connection_manager
from datetime import datetime
import asyncio


def upsert_portfolio(db: Session, user_id: int, broker_account_id: int, positions: list[dict]):
    """Delete existing positions and insert new ones."""
    db.query(Portfolio).filter_by(user_id=user_id, broker_account_id=broker_account_id).delete()
    for p in positions:
        db.add(Portfolio(user_id=user_id, broker_account_id=broker_account_id, **p))
    db.commit()


def upsert_account_summary(db: Session, user_id: int, broker_account_id: int, summary: dict):
    """Delete existing summary and insert new one."""
    db.query(AccountSummary).filter_by(user_id=user_id, broker_account_id=broker_account_id).delete()
    db.add(AccountSummary(user_id=user_id, broker_account_id=broker_account_id, **summary))
    db.commit()


def upsert_trades(db: Session, user_id: int, broker_account_id: int, trades: list[dict]):
    """Insert only new trades (skip existing exec_ids)."""
    existing_exec_ids = {t.exec_id for t in db.query(Trade.exec_id)
                         .filter_by(broker_account_id=broker_account_id)}
    for t in trades:
        if t["exec_id"] not in existing_exec_ids:
            db.add(Trade(user_id=user_id, broker_account_id=broker_account_id, **t))
    db.commit()


async def sync_broker_data(broker_account_id: int, user_id: int):
    """
    Background task to sync data from IBKR.
    Fetches positions, account summary, and trade executions.
    """
    db: Session = SessionLocal()
    try:
        print(f"🔄 Starting sync for broker account {broker_account_id}")

        broker_account = db.query(BrokerAccount).filter_by(id=broker_account_id).first()
        if not broker_account:
            print(f"❌ Broker account {broker_account_id} not found")
            return

        # Get connection
        ib = await connection_manager.get_or_create_connection(broker_account)

        # Fetch positions
        print(f"  📊 Fetching positions...")
        positions = await ib.reqPositionsAsync()
        positions_data = [
            {
                "symbol": p.contract.symbol,
                "quantity": float(p.position),
                "avg_cost": float(p.avgCost),
                "current_price": None,  # Need market data subscription
                "market_value": float(p.position * p.avgCost),
                "unrealized_pnl": 0.0,
                "realized_pnl": 0.0
            }
            for p in positions
        ]
        upsert_portfolio(db, user_id, broker_account_id, positions_data)
        print(f"  ✅ Synced {len(positions_data)} positions")

        # Fetch account summary
        print(f"  💰 Fetching account summary...")
        summary_items = await ib.reqAccountSummaryAsync()
        summary_dict = {}
        for item in summary_items:
            if item.tag == "TotalCashValue":
                summary_dict["total_cash"] = float(item.value)
            elif item.tag == "NetLiquidation":
                summary_dict["net_liquidation"] = float(item.value)
            elif item.tag == "EquityWithLoanValue":
                summary_dict["equity_with_loan"] = float(item.value)
            elif item.tag == "BuyingPower":
                summary_dict["buying_power"] = float(item.value)

        if summary_dict:
            upsert_account_summary(db, user_id, broker_account_id, summary_dict)
            print(f"  ✅ Synced account summary")

        # Fetch executions (trades)
        print(f"  📈 Fetching trade executions...")
        executions = await ib.reqExecutionsAsync()
        trades_data = [
            {
                "exec_id": e.execution.execId,
                "order_id": str(e.execution.orderId),
                "symbol": e.contract.symbol,
                "side": e.execution.side,
                "qty": float(e.execution.shares),
                "price": float(e.execution.price),
                "realized_pnl": float(e.commissionReport.realizedPNL) if e.commissionReport else None,
                "trade_time": datetime.strptime(e.execution.time, "%Y%m%d  %H:%M:%S")
            }
            for e in executions
        ]
        upsert_trades(db, user_id, broker_account_id, trades_data)
        print(f"  ✅ Synced {len(trades_data)} trades")

        # Update broker account timestamp
        broker_account.updated_at = datetime.utcnow()
        db.commit()

        print(f"✅ Sync completed for broker account {broker_account_id}")

    except Exception as e:
        print(f"❌ Sync error for broker_account {broker_account_id}: {e}")
        db.rollback()
    finally:
        db.close()