from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from app.api.schemas import ChatRequest, ChatResponse, UploadReceiptResponse
from app.core.runtime import run_agent
from app.core.settings import settings
from app.core.db import init_db
from app.api.db_dep import get_db

import logging
from typing import Iterable, List, Optional, Dict, Any
from app.services.receipt import parse_receipt_bytes, guess_category
from app.services.expense_service import add_expense
from app.core.db import SessionLocal
from datetime import datetime
from app.api.schemas import ReceiptItem
from app.core.llm_fallback import ask_gemini
from app.services.tools import (
    tool_add_expense, tool_total_spend, tool_summary_by_category, tool_rag_search
)
from pathlib import Path
import json

# NEW: use RAG directly (not the ADK tool wrapper)
from app.services.rag import search as rag_search
from app.services.rag_bootstrap import ensure_seed
import re

CATEGORIES = ["Groceries","Dining","Transport","Utilities","Shopping","Health","Entertainment","Other"]
_TRIGGERS = [
    "what categories","supported categories","support categories",
    "list of categories","expense categories","categories do you support",
    "category list","what can you support",
]

log = logging.getLogger("uvicorn.error")

app = FastAPI(title="Multimodal Expense Assistant API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("db/uploads"); UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.on_event("startup")
async def _startup():
    await init_db()
    try:
        if ensure_seed():
            log.info("RAG index seeded.")
    except Exception as e:
        log.warning(f"RAG seed skipped: {e}")
    log.info("DB initialized.")

@app.get("/healthz")
def healthz():
    ok = bool(settings.GOOGLE_API_KEY) and bool(settings.GENAI_MODEL)
    return {"ok": ok, "model": settings.GENAI_MODEL}

def _extract_text_from_events(events: Iterable) -> str:
    chunks = []
    for e in events:
        etype = type(e).__name__
        log.info(f"[ADK] event type: %s", etype)
        content = getattr(e, "content", None)
        if content is not None:
            parts = getattr(content, "parts", None)
            if parts:
                for p in parts:
                    t = getattr(p, "text", None)
                    if t:
                        chunks.append(t)
        t = getattr(e, "text", None)
        if isinstance(t, str) and t.strip():
            chunks.append(t)
        msgs = getattr(e, "messages", None)
        if msgs:
            for m in msgs:
                mt = getattr(m, "text", None)
                if isinstance(mt, str) and mt.strip():
                    chunks.append(mt)
    return "\n".join([c for c in chunks if c]).strip()

def _format_categories() -> str:
    bullets = "\n".join(f"- {c}" for c in CATEGORIES)
    return f"I support these categories:\n{bullets}\n\n(From internal guidance.)"

def _categories_from_rag() -> str | None:
    try:
        hits = rag_search("categories", k=8)   # use k, not n_results
    except Exception as e:
        # Optional: log here if you want
        return None
    if not hits:
        return None
    text_blob = " ".join(h.get("text","") for h in hits)
    score = sum(1 for c in CATEGORIES if c.lower() in text_blob.lower())
    return _format_categories() if score >= len(CATEGORIES)//2 else None

def _is_category_intent(q: str) -> bool:
    ql = q.lower()
    return any(t in ql for t in _TRIGGERS)

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # short-circuit categories intent with deterministic answer
    if _is_category_intent(req.message):
        return ChatResponse(text=_categories_from_rag() or _format_categories())

    text = ""
    try:
        events = await run_agent(session_id=req.session_id, message_content=req.message)
        text = _extract_text_from_events(events)
    except Exception as e:
        log.exception("ADK run failed: %s", e)

    if not text:
        log.warning("ADK returned no text; using Gemini fallback.")
        text = ask_gemini(req.message)

    return ChatResponse(text=text or "Sorry, I couldn’t produce a response.")

@app.post("/api/upload-receipt", response_model=UploadReceiptResponse)
async def upload_receipt(file: UploadFile = File(...), db=Depends(get_db)):
    if not file.content_type or not file.content_type.startswith(("image/")):
        # keep images for now; PDFs can be added later with pdf->image conversion
        raise HTTPException(status_code=400, detail="Upload a receipt image (png/jpg/webp/heic).")

    # 1) persist file
    dest = UPLOAD_DIR / file.filename
    data = await file.read()
    dest.write_bytes(data)

    # 2) parse with Gemini (structured output)
    parsed = parse_receipt_bytes(data, file.content_type)

    # 3) choose category (model guess, else heuristic)
    category = parsed.get("category_guess") or guess_category(parsed.get("vendor", ""), "Other")

    # 4) insert 1 row (aggregate total); keep raw json for audit
    e = await add_expense(
        db,
        date_=datetime.fromisoformat(parsed["transaction_date"]).date(),
        vendor=parsed["vendor"],
        category=category,
        amount=float(parsed["total"]),
        currency=parsed.get("currency") or "USD",
        notes=None,
        raw_text=json.dumps(parsed, ensure_ascii=False),
        receipt_path=str(dest),
    )

    return UploadReceiptResponse(
        ok=True,
        note=f"Parsed and saved '{file.filename}'.",
        vendor=parsed["vendor"],
        transaction_date=parsed["transaction_date"],
        total=float(parsed["total"]),
        currency=parsed.get("currency") or "USD",
        category=category,
        items=parsed.get("items", []),
        inserted_id=e.id,
        confidence=float(parsed.get("confidence", 0.0)),
    )

# ------ Simple REST helpers for testing tools without the agent ------
@app.post("/api/expense")
async def api_add_expense(
    amount: float, date_str: str, vendor: str, category: str,
    currency: str="USD", notes: Optional[str]=None,
    db=Depends(get_db)
):
    return await tool_add_expense(db, amount=amount, date_str=date_str, vendor=vendor,
                                  category=category, currency=currency, notes=notes)

@app.get("/api/summary/total")
async def api_total_spend(
    start: Optional[str]=Query(None), end: Optional[str]=Query(None),
    category: Optional[str]=Query(None), db=Depends(get_db)
):
    return await tool_total_spend(db, start=start, end=end, category=category)

@app.get("/api/summary/by-category")
async def api_summary_by_category(
    start: Optional[str]=Query(None), end: Optional[str]=Query(None), db=Depends(get_db)
):
    return await tool_summary_by_category(db, start=start, end=end)

@app.get("/api/rag/search")
def api_rag_search(q: str, k: int=5):
    return tool_rag_search(query=q, k=k)