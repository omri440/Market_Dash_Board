from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import relationship
from backend.db import Base

class AccountSummary(Base):
    __tablename__ = "account_summary"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    broker_account_id = Column(Integer, ForeignKey("broker_accounts.id", ondelete="CASCADE"), nullable=False)

    total_cash = Column(Float, nullable=True)
    net_liquidation = Column(Float, nullable=True)
    equity_with_loan = Column(Float, nullable=True)
    buying_power = Column(Float, nullable=True)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="account_summaries")
    broker_account = relationship("BrokerAccount", back_populates="account_summaries")

    __table_args__ = (
        Index("ix_acctsum_user_ba", "user_id", "broker_account_id"),
    )
