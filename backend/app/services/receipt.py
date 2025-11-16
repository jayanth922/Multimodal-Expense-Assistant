from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime
import json
from google import genai
from google.genai import types
from app.core.settings import settings

client = genai.Client(api_key=settings.GOOGLE_API_KEY)

RECEIPT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "transaction_date": {"type": ["string", "null"], "format": "date",
                             "description": "Purchase date in YYYY-MM-DD, or null if uncertain."},
        "vendor": {"type": "string", "description": "Store/merchant name; no address unless part of vendor name."},
        "total": {"type": "number", "description": "Final total paid inclusive of taxes/fees."},
        "currency": {"type": "string", "description": "ISO currency code if shown; otherwise guess (e.g., USD)."},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "quantity": {"type": ["number", "null"]},
                    "unit_price": {"type": ["number", "null"]},
                    "amount": {"type": ["number", "null"]}
                },
                "required": ["description"]
            }
        },
        "category_guess": {"type": ["string", "null"],
                           "description": "One of Groceries, Dining, Transport, Utilities, Shopping, Health, Entertainment, Other."},
        "confidence": {"type": "number", "description": "0..1 overall confidence in parsed fields."}
    },
    "required": ["vendor", "total"]
}

PROMPT = (
    "Extract key fields from this receipt image. "
    "Only use the schema; do not add extra keys. If a value is missing, use null. "
    "Prefer the printed total as 'total'. If multiple totals, choose the customer charge.\n"
    "Categories: Groceries, Dining, Transport, Utilities, Shopping, Health, Entertainment, Other."
)

def _coerce_date(d: str | None) -> str:
    if not d:
        return datetime.utcnow().date().isoformat()
    try:
        return datetime.fromisoformat(d).date().isoformat()
    except Exception:
        # Try common alternatives
        for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(d, fmt).date().isoformat()
            except Exception:
                pass
    return datetime.utcnow().date().isoformat()

def parse_receipt_bytes(image_bytes: bytes, mime_type: str) -> Dict[str, Any]:
    """Return dict conforming to RECEIPT_SCHEMA."""
    resp = client.models.generate_content(
        model=settings.GENAI_MODEL,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            PROMPT,
        ],
        config={
            "response_mime_type": "application/json",
            "response_json_schema": RECEIPT_SCHEMA,
        },
    )
    data = json.loads(resp.text) if getattr(resp, "text", None) else {}
    # safety net defaults
    data.setdefault("vendor", "Unknown")
    data.setdefault("currency", "USD")
    data["transaction_date"] = _coerce_date(data.get("transaction_date"))
    data["category_guess"] = data.get("category_guess") or "Other"
    data["confidence"] = float(data.get("confidence") or 0.0)
    if not isinstance(data.get("items"), list):
        data["items"] = []
    return data

# very small heuristic for vendor->category
def guess_category(vendor: str, fallback: str = "Other") -> str:
    v = (vendor or "").lower()
    if any(k in v for k in ["uber", "lyft", "shell", "chevron", "exxon", "bp", "metro", "bus"]):
        return "Transport"
    if any(k in v for k in ["starbucks", "cafe", "coffee", "restaurant", "grill", "pizza", "chipotle", "mcdonald", "burger", "ubereats", "doordash"]):
        return "Dining"
    if any(k in v for k in ["walmart", "target", "best buy", "amazon", "costco"]):
        return "Shopping"
    if any(k in v for k in ["kroger", "whole foods", "safeway", "aldi", "trader joe", "grocery"]):
        return "Groceries"
    if any(k in v for k in ["comcast", "xfinity", "att", "verizon", "pg&e", "electric", "water"]):
        return "Utilities"
    if any(k in v for k in ["pharmacy", "walgreens", "cvs", "rite aid", "clinic", "dental"]):
        return "Health"
    if any(k in v for k in ["netflix", "spotify", "hulu", "cinema", "theater"]):
        return "Entertainment"
    return fallback