from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AccountSummaryBase(BaseModel):
    total_cash: Optional[float]
    net_liquidation: Optional[float]
    equity_with_loan: Optional[float]
    buying_power: Optional[float]

class AccountSummaryCreate(AccountSummaryBase):
    broker_account_id: int

class AccountSummaryResponse(AccountSummaryBase):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True
