"""SQL Validation & Safety Agent.

Deterministic validation + optional LLM-based rewrite loop can be added.
For enterprise guardrails, deterministic checks run BEFORE any execution.
"""

from __future__ import annotations

from dataclasses import dataclass

from text2sql_app.core.sql_safety import SafetyResult, validate_and_rewrite


@dataclass
class ValidationOutcome:
    ok: bool
    sql: str
    reason: str = ""


class SQLValidationAgent:
    def run(self, sql: str, max_rows: int, blocked_columns: set[str]) -> ValidationOutcome:
        res: SafetyResult = validate_and_rewrite(sql, max_rows=max_rows, blocked_columns=blocked_columns)
        if not res.ok:
            return ValidationOutcome(ok=False, sql=sql, reason=res.reason)
        return ValidationOutcome(ok=True, sql=res.rewritten_sql or sql, reason="")