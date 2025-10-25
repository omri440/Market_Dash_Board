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

        # 🔥 Trigger initial data sync in background
        print(f"🔄 Triggering initial sync for broker account {broker_account.id}")
        asyncio.create_task(sync_broker_data(broker_account.id, user.id))

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


@router.delete("/disconnect/{broker_account_id}")
async def disconnect_broker(
        broker_account_id: int,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Disconnect and delete a broker account.
    Closes IBKR connection and deletes from database (cascades to related records).
    """
    broker_account = db.query(BrokerAccount).filter_by(
        id=broker_account_id,
        user_id=user.id
    ).first()

    if not broker_account:
        raise HTTPException(status_code=404, detail="Broker account not found")

    # Disconnect from IBKR
    await connection_manager.disconnect(broker_account_id)

    # Delete from database (cascade deletes related records)
    db.delete(broker_account)
    db.commit()

    print(f"🗑️ Broker account {broker_account_id} deleted")
    return {
        "status": "disconnected",
        "broker_account_id": broker_account_id,
        "message": "Broker account disconnected and deleted"
    }


@router.get("/status/{broker_account_id}")
async def get_connection_status(
        broker_account_id: int,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Get connection status for a broker account.
    Returns both database status and live connection status.
    """
    broker_account = db.query(BrokerAccount).filter_by(
        id=broker_account_id,
        user_id=user.id
    ).first()

    if not broker_account:
        raise HTTPException(status_code=404, detail="Broker account not found")

    # Get connection status from manager
    status = connection_manager.get_connection_status(broker_account_id)

    return {
        "broker_account_id": broker_account_id,
        "db_status": broker_account.status,
        "connection_exists": status["exists"],
        "connection_active": status["connected"],
        "connected_at": broker_account.connected_at
    }


@router.get("/quote/{symbol}")
async def get_quote(
        symbol: str,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Get live market quote for a symbol from IBKR.

    Args:
        symbol: Stock symbol (e.g., "AAPL", "GOOGL")
        user: Authenticated user
        db: Database session

    Returns:
        dict: Quote data with last price, bid, ask, volume, etc.

    Example:
        GET /api/broker/quote/AAPL
        Response: {
            "symbol": "AAPL",
            "last": 175.50,
            "bid": 175.48,
            "ask": 175.52,
            "volume": 1234567,
            "high": 176.20,
            "low": 174.80,
            "close": 175.00
        }
    """
    # Get user's first active broker account
    broker_account = db.query(BrokerAccount).filter_by(
        user_id=user.id,
        status="active"
    ).first()

    if not broker_account:
        raise HTTPException(
            status_code=404,
            detail="No active broker account found. Please connect to a broker first."
        )

    try:
        # Get IBKR connection
        ib = await connection_manager.get_or_create_connection(broker_account)

        # Create contract for the symbol
        from ib_async import Stock
        contract = Stock(symbol, 'SMART', 'USD')

        # Qualify the contract (get full contract details)
        contracts = await ib.qualifyContractsAsync(contract)
        if not contracts:
            raise HTTPException(
                status_code=404,
                detail=f"Symbol '{symbol}' not found or invalid"
            )

        qualified_contract = contracts[0]

        # Request market data
        ticker = ib.reqMktData(qualified_contract, '', False, False)

        # Wait for data to arrive (max 3 seconds)
        await asyncio.sleep(3)

        # Check if we got valid data
        if ticker.last is None or ticker.last == 0:
            # Try to get data from close price if last is not available
            if ticker.close and ticker.close > 0:
                last_price = ticker.close
            else:
                raise HTTPException(
                    status_code=503,
                    detail=f"No market data available for '{symbol}'. Market may be closed or symbol requires subscription."
                )
        else:
            last_price = ticker.last

        # Cancel market data subscription to avoid data fees
        ib.cancelMktData(qualified_contract)

        return {
            "symbol": symbol,
            "last": float(last_price) if last_price else None,
            "bid": float(ticker.bid) if ticker.bid and ticker.bid > 0 else None,
            "ask": float(ticker.ask) if ticker.ask and ticker.ask > 0 else None,
            "volume": int(ticker.volume) if ticker.volume else None,
            "high": float(ticker.high) if ticker.high and ticker.high > 0 else None,
            "low": float(ticker.low) if ticker.low and ticker.low > 0 else None,
            "close": float(ticker.close) if ticker.close and ticker.close > 0 else None,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting quote for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get quote for '{symbol}': {str(e)}"
        )