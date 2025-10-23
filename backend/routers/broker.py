from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.models.user import User
from backend.models.broker_account import BrokerAccount
from backend.schemas.broker_account import BrokerAccountCreate, BrokerAccountResponse
from backend.utils.auth_dependency import get_current_user
from backend.services.ibkr_connection_manager import connection_manager
from backend.services.ibkr_sync import sync_broker_data
from datetime import datetime
import asyncio

router = APIRouter(prefix="/api/broker", tags=["Broker"])


@router.post("/connect", response_model=BrokerAccountResponse)
async def connect_broker(
        account: BrokerAccountCreate,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Connect to broker and save account.
    Tests connection before saving to DB.
    """
    # Check if already exists
    existing = db.query(BrokerAccount).filter_by(
        user_id=user.id,
        broker=account.broker,
        account_code=account.account_code
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Broker account already connected")

    # Create broker account record
    broker_account = BrokerAccount(
        user_id=user.id,
        broker=account.broker,
        account_code=account.account_code,
        conn_host=account.conn_host,
        conn_port=account.conn_port,
        client_id=account.client_id,
        status="pending"
    )
    db.add(broker_account)
    db.commit()
    db.refresh(broker_account)

    # Test connection
    try:
        ib = await connection_manager.get_or_create_connection(broker_account)

        # Update status
        broker_account.status = "active"
        broker_account.connected_at = datetime.utcnow()
        db.commit()
        db.refresh(broker_account)

        return broker_account
    except Exception as e:
        broker_account.status = "error"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")


@router.post("/sync/{broker_account_id}")
async def sync_broker_account(
        broker_account_id: int,
        background_tasks: BackgroundTasks,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Trigger sync for a broker account.
    Runs in background task.
    """
    broker_account = db.query(BrokerAccount).filter_by(
        id=broker_account_id,
        user_id=user.id
    ).first()

    if not broker_account:
        raise HTTPException(status_code=404, detail="Broker account not found")

    # Add background task
    background_tasks.add_task(sync_broker_data, broker_account.id, user.id)

    return {"status": "sync_started", "broker_account_id": broker_account_id}


@router.get("/accounts", response_model=list[BrokerAccountResponse])
def get_broker_accounts(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get all broker accounts for current user."""
    accounts = db.query(BrokerAccount).filter_by(user_id=user.id).all()
    return accounts