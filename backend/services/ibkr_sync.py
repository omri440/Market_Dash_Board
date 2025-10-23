from sqlalchemy.orm import Session
from backend.models.portfolio import Portfolio
from backend.models.trade import Trade
from backend.models.account_summary import AccountSummary
from backend.models.broker_account import BrokerAccount

def upsert_portfolio(db: Session, user_id: int, broker_account_id: int, positions: list[dict]):
    db.query(Portfolio).filter_by(user_id=user_id, broker_account_id=broker_account_id).delete()
    for p in positions:
        db.add(Portfolio(user_id=user_id, broker_account_id=broker_account_id, **p))
    db.commit()

def upsert_account_summary(db: Session, user_id: int, broker_account_id: int, summary: dict):
    db.query(AccountSummary).filter_by(user_id=user_id, broker_account_id=broker_account_id).delete()
    db.add(AccountSummary(user_id=user_id, broker_account_id=broker_account_id, **summary))
    db.commit()

def upsert_trades(db: Session, user_id: int, broker_account_id: int, trades: list[dict]):
    existing_exec_ids = {t.exec_id for t in db.query(Trade.exec_id)
                         .filter_by(broker_account_id=broker_account_id)}
    for t in trades:
        if t["exec_id"] not in existing_exec_ids:
            db.add(Trade(user_id=user_id, broker_account_id=broker_account_id, **t))
    db.commit()
