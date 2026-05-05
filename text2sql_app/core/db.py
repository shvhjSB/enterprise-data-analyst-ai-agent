"""Database access layer.

- Async SQLAlchemy engine creation
- Safe reflection/introspection
- Query execution with timeouts and row limits

Supports any SQLAlchemy-compatible DB URL. For local tests/examples, we use:
  sqlite+aiosqlite:///./example.db
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import MetaData, text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from text2sql_app.core.config import get_settings


@dataclass
class DBHandle:
    db_id: str
    url: str


def create_engine(db_url: str) -> AsyncEngine:
    # pool_pre_ping improves resilience
    return create_async_engine(db_url, pool_pre_ping=True, future=True)


async def test_connection(db_url: str) -> None:
    engine = create_engine(db_url)
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    await engine.dispose()


async def reflect_schema(db_url: str, schema: str | None = None) -> MetaData:
    engine = create_engine(db_url)
    md = MetaData(schema=schema)
    async with engine.connect() as conn:
        await conn.run_sync(md.reflect)
    await engine.dispose()
    return md


async def execute_sql(
    db_url: str,
    sql: str,
    params: Optional[Dict[str, Any]] = None,
    timeout_s: Optional[int] = None,
    max_rows: Optional[int] = None,
) -> Tuple[List[str], List[Tuple[Any, ...]], float]:
    settings = get_settings()
    timeout_s = timeout_s or settings.text2sql_app_query_timeout_seconds
    max_rows = max_rows or settings.text2sql_app_max_rows

    engine = create_engine(db_url)
    start = asyncio.get_event_loop().time()

    async def _run() -> Tuple[List[str], List[Tuple[Any, ...]]]:
        async with engine.connect() as conn:
            result = await conn.execute(text(sql), params or {})
            rows = result.fetchmany(size=max_rows)
            cols = list(result.keys())
            return cols, rows

    try:
        cols, rows = await asyncio.wait_for(_run(), timeout=timeout_s)
    finally:
        await engine.dispose()

    elapsed = asyncio.get_event_loop().time() - start
    return cols, rows, elapsed