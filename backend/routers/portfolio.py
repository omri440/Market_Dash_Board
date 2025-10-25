from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.models.user import User
from backend.models.portfolio import Portfolio
from backend.models.trade import Trade
from backend.models.account_summary import AccountSummary
from backend.schemas.portfolio import PortfolioResponse
from backend.schemas.trade import TradeResponse
from backend.schemas.account_summary import AccountSummaryResponse
from backend.utils.auth_dependency import get_current_user
from typing import List

router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])


@router.get("/", response_model=List[PortfolioResponse])
def get_portfolio(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all portfolio positions for the authenticated user.
    Returns positions from all connected broker accounts.
    """
    positions = db.query(Portfolio).filter_by(user_id=user.id).all()
    return positions


@router.get("/broker/{broker_account_id}", response_model=List[PortfolioResponse])
def get_portfolio_by_broker(
    broker_account_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get portfolio positions for a specific broker account.
    """
    # Verify broker account belongs to user
    from backend.models.broker_account import BrokerAccount
    broker_account = db.query(BrokerAccount).filter_by(
        id=broker_account_id,
        user_id=user.id
    ).first()

    if not broker_account:
        raise HTTPException(status_code=404, detail="Broker account not found")

    positions = db.query(Portfolio).filter_by(
        user_id=user.id,
        broker_account_id=broker_account_id
    ).all()

    return positions


@router.get("/trades", response_model=List[TradeResponse])
def get_trades(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 100
):
    """
    Get recent trades for the authenticated user.
    """
    trades = (
        db.query(Trade)
        .filter_by(user_id=user.id)
        .order_by(Trade.trade_time.desc())
        .limit(limit)
        .all()
    )
    return trades


@router.get("/account-summary", response_model=List[AccountSummaryResponse])
def get_account_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get account summary for all broker accounts.
    """
    summaries = db.query(AccountSummary).filter_by(user_id=user.id).all()
    return summaries


@router.get("/account-summary/{broker_account_id}", response_model=AccountSummaryResponse)
def get_account_summary_by_broker(
    broker_account_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get account summary for a specific broker account.
    """
    # Verify broker account belongs to user
    from backend.models.broker_account import BrokerAccount
    broker_account = db.query(BrokerAccount).filter_by(
        id=broker_account_id,
        user_id=user.id
    ).first()

    if not broker_account:
        raise HTTPException(status_code=404, detail="Broker account not found")

    summary = db.query(AccountSummary).filter_by(
        user_id=user.id,
        broker_account_id=broker_account_id
    ).first()

    if not summary:
        raise HTTPException(status_code=404, detail="Account summary not found")

    return summary
