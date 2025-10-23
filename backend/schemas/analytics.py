from pydantic import BaseModel
from typing import List
from datetime import date

class EquityPoint(BaseModel):
    date: date
    equity: float

class AnalyticsResponse(BaseModel):
    total_trades: int
    win_rate: float
    avg_profit: float
    equity_curve: List[EquityPoint]
