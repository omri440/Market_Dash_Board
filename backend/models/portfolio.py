from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from backend.db import Base

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    broker_account_id = Column(Integer, ForeignKey("broker_accounts.id", ondelete="CASCADE"), nullable=False)

    symbol = Column(String, nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    avg_cost = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    market_value = Column(Float, nullable=True)
    unrealized_pnl = Column(Float, nullable=True)
    realized_pnl = Column(Float, nullable=True)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="portfolio")
    broker_account = relationship("BrokerAccount", back_populates="portfolios")

    __table_args__ = (
        UniqueConstraint("user_id", "broker_account_id", "symbol", name="uq_portfolio_user_ba_symbol"),
        Index("ix_portfolio_user_ba", "user_id", "broker_account_id"),
    )
