from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class BrokerName(str, Enum):
    ibkr = "ibkr"
    alpaca = "alpaca"
    dummy = "dummy"

class BrokerAccountBase(BaseModel):
    broker: BrokerName
    account_code: str
    label: Optional[str] = None
    status: Optional[str] = "active"

class BrokerAccountCreate(BrokerAccountBase):
    conn_host: Optional[str] = None
    conn_port: Optional[int] = None
    client_id: Optional[int] = None

class BrokerAccountResponse(BrokerAccountBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
