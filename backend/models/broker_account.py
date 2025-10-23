from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from backend.db import Base
import enum

class BrokerName(str, enum.Enum):
    ibkr = "ibkr"
    alpaca = "alpaca"
    dummy = "dummy"

class BrokerAccount(Base):
    __tablename__ = "broker_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    broker = Column(Enum(BrokerName, name="broker_enum"), nullable=False, index=True)
    account_code = Column(String, nullable=False)  # לדוגמה U1234567

    # פרמטרים לחיבור מקומי ל־TWS/IBGW (אופציונלי)
    conn_host = Column(String, nullable=True)
    conn_port = Column(Integer, nullable=True)
    client_id = Column(Integer, nullable=True)

    status = Column(String, default="active")  # active/paused (אופציונלי)
    label = Column(String, nullable=True)      # תיאור ידידותי (אופציונלי)

    connected_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="broker_accounts")
    portfolios = relationship("Portfolio", back_populates="broker_account", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="broker_account", cascade="all, delete-orphan")
    account_summaries = relationship("AccountSummary", back_populates="broker_account", cascade="all, delete-orphan")
    positions_history = relationship("PositionHistory", back_populates="broker_account", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("user_id", "broker", "account_code", name="uq_user_broker_accountcode"),
    )
