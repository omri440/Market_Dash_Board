from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import relationship
from backend.db import Base

class PositionHistory(Base):
    __tablename__ = "positions_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    broker_account_id = Column(Integer, ForeignKey("broker_accounts.id", ondelete="CASCADE"), nullable=False)

    symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    market_price = Column(Float, nullable=True)
    unrealized_pnl = Column(Float, nullable=True)
    realized_pnl = Column(Float, nullable=True)

    ts = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="positions_history")
    broker_account = relationship("BrokerAccount", back_populates="positions_history")

    __table_args__ = (
        Index("ix_poshist_user_ba_ts", "user_id", "broker_account_id", "ts"),
    )
