from pydantic import BaseModel
from datetime import datetime

class JournalBase(BaseModel):
    symbol: str
    side: str
    qty: int
    entry: float
    exit: float | None = None
    profit: float | None = None

class JournalCreate(JournalBase):
    pass

class JournalResponse(JournalBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
