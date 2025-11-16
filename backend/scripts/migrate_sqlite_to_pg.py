import os, asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from pathlib import Path

SQLITE_PATH = os.getenv("SQLITE_PATH", "./db/expenses.sqlite")
PG_URL = os.getenv("DATABASE_URL")

def norm_pg(url: str) -> str:
    import urllib.parse as up
    url = url.replace("postgres://", "postgresql://")
    if url.startswith("postgresql://") and "+psycopg" not in url and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    # For psycopg/libpq, ensure ssl + TCP keepalives (Neon-friendly)
    if "+psycopg" in url:
        p = up.urlparse(url)
        q = dict(up.parse_qsl(p.query, keep_blank_values=True))
        q.setdefault("sslmode", "require")
        q.setdefault("keepalives", "1")
        q.setdefault("keepalives_idle", "30")
        q.setdefault("keepalives_interval", "10")
        q.setdefault("keepalives_count", "5")
        url = up.urlunparse(p._replace(query=up.urlencode(q)))
    return url

async def main():
    if not PG_URL:
        raise SystemExit("Set DATABASE_URL for the target Postgres.")
    # read from sqlite (sync)
    import sqlite3, json
    sp = Path(SQLITE_PATH).resolve()
    if not sp.exists():
        print("No SQLite file found; nothing to migrate.")
        return
    rows = []
    con = sqlite3.connect(str(sp))
    try:
        for r in con.execute("select id,date,vendor,category,amount,currency,notes,raw_text,receipt_path from expenses"):
            rows.append(r)
    finally:
        con.close()

    if not rows:
        print("No rows to migrate.")
        return

    # write to PG (async)
    pg = create_async_engine(norm_pg(PG_URL), echo=False, future=True)
    async with pg.begin() as conn:
        # ensure table exists
        await conn.execute(text("""
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            vendor VARCHAR(128) NOT NULL,
            category VARCHAR(64) NOT NULL,
            amount DOUBLE PRECISION NOT NULL,
            currency VARCHAR(8) NOT NULL DEFAULT 'USD',
            notes TEXT NULL,
            raw_text TEXT NULL,
            receipt_path TEXT NULL
        )"""))
        for r in rows:
            await conn.execute(
                text("""INSERT INTO expenses (date,vendor,category,amount,currency,notes,raw_text,receipt_path)
                        VALUES (:date,:vendor,:category,:amount,:currency,:notes,:raw_text,:receipt_path)"""),
                dict(date=r[1], vendor=r[2], category=r[3], amount=r[4], currency=r[5],
                     notes=r[6], raw_text=r[7], receipt_path=r[8])
            )
    print(f"Migrated {len(rows)} rows to Postgres.")

if __name__ == "__main__":
    asyncio.run(main())