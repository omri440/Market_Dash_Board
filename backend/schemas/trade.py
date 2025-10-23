from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TradeBase(BaseModel):
    symbol: str
    side: str
    qty: float
    price: float
    realized_pnl: Optional[float]
    trade_time: datetime

class TradeCreate(TradeBase):
    broker_account_id: int
    exec_id: Optional[str]
    order_id: Optional[str]

class TradeResponse(TradeBase):
    id: int

    class Config:
        orm_mode = True
