from __future__ import annotations
from datetime import date
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.expense import Expense

async def add_expense(db: AsyncSession, *, date_: date, vendor: str, category: str,
                      amount: float, currency: str="USD", notes: Optional[str]=None,
                      raw_text: Optional[str]=None, receipt_path: Optional[str]=None) -> Expense:
    e = Expense(date=date_, vendor=vendor, category=category, amount=amount, currency=currency,
                notes=notes, raw_text=raw_text, receipt_path=receipt_path)
    db.add(e)
    await db.commit()
    await db.refresh(e)
    return e

async def list_expenses(db: AsyncSession, *, start: Optional[date]=None, end: Optional[date]=None,
                        category: Optional[str]=None) -> List[Expense]:
    stmt = select(Expense)
    if start:
        stmt = stmt.where(Expense.date >= start)
    if end:
        stmt = stmt.where(Expense.date <= end)
    if category:
        stmt = stmt.where(Expense.category.ilike(category))
    stmt = stmt.order_by(Expense.date.desc(), Expense.id.desc())
    res = await db.execute(stmt)
    return list(res.scalars().all())

async def summary_by_category(db: AsyncSession, *, start: Optional[date]=None, end: Optional[date]=None) -> List[Dict[str, Any]]:
    stmt = select(Expense.category, func.sum(Expense.amount)).group_by(Expense.category)
    if start:
        stmt = stmt.where(Expense.date >= start)
    if end:
        stmt = stmt.where(Expense.date <= end)
    res = await db.execute(stmt)
    return [{"category": c, "total": float(t or 0)} for c, t in res.all()]

async def total_spend(db: AsyncSession, *, start: Optional[date]=None, end: Optional[date]=None, category: Optional[str]=None) -> float:
    stmt = select(func.sum(Expense.amount))
    if start:
        stmt = stmt.where(Expense.date >= start)
    if end:
        stmt = stmt.where(Expense.date <= end)
    if category:
        stmt = stmt.where(Expense.category.ilike(category))
    res = await db.execute(stmt)
    return float(res.scalar() or 0.0)
