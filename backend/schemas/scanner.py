from pydantic import BaseModel

class ScannerResponse(BaseModel):
    symbol: str
    price: float
    change_pct: float
    volume: int
