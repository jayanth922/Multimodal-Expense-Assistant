from __future__ import annotations
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.expense_service import add_expense, list_expenses, total_spend, summary_by_category
from app.services.rag import search as rag_search

def _parse_date(s: str) -> date:
    return datetime.fromisoformat(s).date()

async def tool_add_expense(
    db: AsyncSession, *,
    amount: float, date_str: str, vendor: str, category: str,
    currency: str = "USD", notes: Optional[str] = None
) -> Dict[str, Any]:
    e = await add_expense(db, date_=_parse_date(date_str), vendor=vendor, category=category,
                          amount=amount, currency=currency, notes=notes)
    return {"ok": True, "id": e.id}

async def tool_total_spend(
    db: AsyncSession, *, start: Optional[str] = None, end: Optional[str] = None, category: Optional[str] = None
) -> Dict[str, Any]:
    s = _parse_date(start) if start else None
    e = _parse_date(end) if end else None
    total = await total_spend(db, start=s, end=e, category=category)
    return {"total": total, "currency": "USD"}

async def tool_summary_by_category(
    db: AsyncSession, *, start: Optional[str] = None, end: Optional[str] = None
) -> List[Dict[str, Any]]:
    s = _parse_date(start) if start else None
    e = _parse_date(end) if end else None
    return await summary_by_category(db, start=s, end=e)

def tool_rag_search(*, query: str, k: int = 5) -> List[Dict[str, Any]]:
    return rag_search(query, k=k)
