"""SQL Generation Agent.

Generates dialect-aware SQL from a plan.
In this scaffold, dialect handling is simple; production would map by SQLAlchemy dialect.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from text2sql_app.core.llm import get_llm


SQL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "sql": {"type": "string"},
        "explanation": {"type": "string"},
    },
    "required": ["sql", "explanation"],
}


@dataclass
class SQLDraft:
    sql: str
    explanation: str


class SQLGenerationAgent:
    async def run(self, plan_json: Dict[str, Any], schema_compact: str, dialect: str) -> SQLDraft:
        llm = get_llm()
        system = (
            "You are a SQL generator for enterprise analytics. "
            "Generate a single SELECT query only (no CTE recursion required unless necessary). "
            "Never use SELECT *. Quote identifiers safely if needed. "
            "Return ONLY JSON matching schema."
        )
        user = (
            f"DB dialect: {dialect}\n\n"
            f"Plan JSON: {plan_json}\n\n"
            f"Schema hints (compact):\n{schema_compact}\n\n"
            "Output SQL + a short explanation."
        )
        res = await llm.complete_json(system=system, user=user, schema=SQL_SCHEMA, temperature=0.0)
        obj = res.json or {}
        return SQLDraft(sql=obj["sql"], explanation=obj["explanation"])