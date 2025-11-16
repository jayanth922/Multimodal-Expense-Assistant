from __future__ import annotations
from typing import AsyncGenerator
from app.core.db import SessionLocal

async def get_db() -> AsyncGenerator:
    async with SessionLocal() as session:
        yield session
