from __future__ import annotations
from typing import Optional, List, Dict, Any
from datetime import datetime, date

from app.core.db import SessionLocal
from app.services.expense_service import add_expense, total_spend, summary_by_category
from app.services.rag import search as rag_search

def _parse_date(s: str) -> date:
    return datetime.fromisoformat(s).date()

# ---------- ADK tools (no DB arg) ----------

async def add_expense_tool(
    amount: float, date_str: str, vendor: str, category: str,
    currency: str = "USD", notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a single expense row. date_str must be ISO (YYYY-MM-DD).
    Returns: {"ok": bool, "id": int}
    """
    async with SessionLocal() as db:
        e = await add_expense(
            db,
            date_=_parse_date(date_str),
            vendor=vendor,
            category=category,
            amount=amount,
            currency=currency,
            notes=notes,
        )
        return {"ok": True, "id": e.id}

async def total_spend_tool(
    start: Optional[str] = None, end: Optional[str] = None, category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Return total spend for an optional date range/category.
    Dates are ISO (YYYY-MM-DD). Returns {"total": float, "currency": "USD"}.
    """
    s = _parse_date(start) if start else None
    e = _parse_date(end) if end else None
    async with SessionLocal() as db:
        total = await total_spend(db, start=s, end=e, category=category)
        return {"total": total, "currency": "USD"}

async def summary_by_category_tool(
    start: Optional[str] = None, end: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Return totals grouped by category in the date range.
    """
    s = _parse_date(start) if start else None
    e = _parse_date(end) if end else None
    async with SessionLocal() as db:
        return await summary_by_category(db, start=s, end=e)

def rag_search_tool(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve top-k guidance snippets relevant to the query.
    """
    return rag_search(query, k=k)