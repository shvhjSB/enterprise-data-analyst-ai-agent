"""SQL validation & safety rules.

- Blocks destructive statements
- Enforces max row limits (best-effort for SQLite/Postgres-like dialects)
- Optional PII column blocking (based on schema + heuristics)

This module is intentionally deterministic and testable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Optional

import sqlparse


DESTRUCTIVE = {
    "drop",
    "delete",
    "truncate",
    "alter",
    "update",
    "insert",
    "create",
    "grant",
    "revoke",
}


@dataclass
class SafetyResult:
    ok: bool
    reason: str = ""
    rewritten_sql: str | None = None


def is_destructive(sql: str) -> bool:
    parsed = sqlparse.parse(sql)
    for stmt in parsed:
        first = stmt.token_first(skip_cm=True)
        if not first:
            continue
        val = first.value.lower()
        if val in DESTRUCTIVE:
            return True
    return False


def enforce_limit(sql: str, max_rows: int) -> str:
    # Best-effort: if query already has LIMIT, keep as-is.
    if re.search(r"\blimit\b", sql, flags=re.IGNORECASE):
        return sql
    # Append LIMIT (works for SQLite/Postgres/MySQL). For SQL Server/Oracle adapt via dialect.
    return sql.rstrip().rstrip(";") + f"\nLIMIT {int(max_rows)};"


def validate_and_rewrite(
    sql: str,
    max_rows: int,
    blocked_columns: Optional[Iterable[str]] = None,
) -> SafetyResult:
    if is_destructive(sql):
        return SafetyResult(ok=False, reason="Destructive statements are not allowed")

    # Very simple PII block: if blocked column appears as a word boundary.
    if blocked_columns:
        for col in blocked_columns:
            if re.search(rf"\b{re.escape(col)}\b", sql, flags=re.IGNORECASE):
                return SafetyResult(ok=False, reason=f"Query references blocked/PII column: {col}")

    rewritten = enforce_limit(sql, max_rows=max_rows)
    return SafetyResult(ok=True, rewritten_sql=rewritten)