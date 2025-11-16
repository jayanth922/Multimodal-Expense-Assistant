from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    text: str

class ReceiptItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None

class UploadReceiptResponse(BaseModel):
    ok: bool
    note: str
    vendor: str | None = None
    transaction_date: str | None = None
    total: float | None = None
    currency: str | None = None
    category: str | None = None
    items: List[ReceiptItem] = []
    inserted_id: Optional[int] = None
    confidence: Optional[float] = None
