from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")

    # קשרים
    broker_accounts = relationship("BrokerAccount", back_populates="user", cascade="all, delete-orphan")
    portfolio = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    journal = relationship("Journal", back_populates="user", cascade="all, delete-orphan")  # אם כבר קיים
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    account_summaries = relationship("AccountSummary", back_populates="user", cascade="all, delete-orphan")
    positions_history = relationship("PositionHistory", back_populates="user", cascade="all, delete-orphan")
