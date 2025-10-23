from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.db import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    broker_account_id = Column(Integer, ForeignKey("broker_accounts.id", ondelete="CASCADE"), nullable=False)

    # מזהי ברוקר — לפחות אחד מהם (תבחר לפי מה שמחזיר ה־API אצלך)
    exec_id = Column(String, nullable=True)
    order_id = Column(String, nullable=True)

    symbol = Column(String, nullable=False, index=True)
    side = Column(String, nullable=False)       # BUY / SELL
    qty = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    realized_pnl = Column(Float, nullable=True)
    trade_time = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="trades")
    broker_account = relationship("BrokerAccount", back_populates="trades")

    __table_args__ = (
        # להבטיח אי-כפילות לפי מזהה ברוקר (תתאים לצורך שלך)
        UniqueConstraint("broker_account_id", "exec_id", name="uq_trade_ba_execid"),
        Index("ix_trade_user_ba_time", "user_id", "broker_account_id", "trade_time"),
    )
