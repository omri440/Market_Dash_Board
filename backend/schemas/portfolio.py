from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PortfolioBase(BaseModel):
    symbol: str
    quantity: float
    avg_cost: float
    current_price: Optional[float] = None
    market_value: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    realized_pnl: Optional[float] = None

class PortfolioCreate(PortfolioBase):
    broker_account_id: int

class PortfolioResponse(PortfolioBase):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True
