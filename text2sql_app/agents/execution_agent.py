"""Execution Agent.

Executes validated SQL and captures execution metadata.
Implements retry loop for transient errors and LLM-guided correction hook.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from tenacity import retry, stop_after_attempt, wait_exponential

from text2sql_app.core.db import execute_sql


@dataclass
class ExecutionResult:
    columns: List[str]
    rows: List[List[Any]]
    execution_time_seconds: float


class ExecutionAgent:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def run(self, db_url: str, sql: str, params: Dict[str, Any] | None = None) -> ExecutionResult:
        cols, rows, elapsed = await execute_sql(db_url=db_url, sql=sql, params=params)
        return ExecutionResult(columns=cols, rows=[list(r) for r in rows], execution_time_seconds=elapsed)