from __future__ import annotations
import os, logging, urllib.parse as up
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from pathlib import Path
from app.core.settings import settings

log = logging.getLogger(__name__)

def _add_query_params(url: str, extra: dict[str, str]) -> str:
    p = up.urlparse(url)
    q = dict(up.parse_qsl(p.query, keep_blank_values=True))
    for k, v in extra.items():
        q.setdefault(k, v)
    return up.urlunparse(p._replace(query=up.urlencode(q)))

def _normalize_db_url(raw: str | None) -> str | None:
    if not raw:
        return None
    url = raw.replace("postgres://", "postgresql://")
    # Default to psycopg driver (works with sslmode=require)
    if url.startswith("postgresql://") and "+psycopg" not in url and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    # For psycopg/libpq, ensure ssl + TCP keepalives (Neon-friendly)
    if "+psycopg" in url:
        url = _add_query_params(url, {
            "sslmode": "require",
            "keepalives": "1",
            "keepalives_idle": "30",
            "keepalives_interval": "10",
            "keepalives_count": "5",
        })
    return url

raw = os.getenv("DATABASE_URL")
DB_URL = _normalize_db_url(raw) if raw else f"sqlite+aiosqlite:///{Path(settings.SQLITE_PATH).resolve()}"

log.info("Using DB_URL: %s", DB_URL.replace("//", "//***:***@"))  # mask credentials

# Key reliability knobs:
# - pool_pre_ping: verifies a connection before each checkout; reconnects if broken
# - pool_recycle: closes & reopens connections periodically (seconds)
# - pool_size/max_overflow: a small, sane pool for dev
engine = create_async_engine(
    DB_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_recycle=900,   # 15 minutes
    pool_size=5,
    max_overflow=10,
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

engine = create_async_engine(DB_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
