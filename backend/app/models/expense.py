from __future__ import annotations
from sqlalchemy import String, Integer, Float, Text, Date, Column
from app.core.db import Base

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    vendor = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False, default="USD")
    notes = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    receipt_path = Column(Text, nullable=True)
