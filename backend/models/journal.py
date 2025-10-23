from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from backend.db import Base

class Journal(Base):
    __tablename__ = "journal"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # BUY / SELL
    qty = Column(Integer, nullable=False)
    entry = Column(Float, nullable=False)
    exit = Column(Float, nullable=True)
    profit = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="journal")
