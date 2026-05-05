"""SQL Planning Agent.

Produces a query plan (tables, joins, group by, aggregations) without emitting SQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from text2sql_app.core.llm import get_llm


PLAN_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "tables": {"type": "array", "items": {"type": "string"}},
        "joins": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "left_table": {"type": "string"},
                    "right_table": {"type": "string"},
                    "on": {"type": "string"},
                    "type": {"type": "string"},
                },
                "required": ["left_table", "right_table", "on", "type"],
            },
        },
        "select": {"type": "array", "items": {"type": "string"}},
        "where": {"type": "array", "items": {"type": "string"}},
        "group_by": {"type": "array", "items": {"type": "string"}},
        "order_by": {"type": "array", "items": {"type": "string"}},
        "limit": {"type": "integer"},
        "notes": {"type": "string"},
    },
    "required": ["tables", "joins", "select", "where", "group_by", "order_by", "limit", "notes"],
}


@dataclass
class SQLPlan:
    tables: List[str]
    joins: List[Dict[str, Any]]
    select: List[str]
    where: List[str]
    group_by: List[str]
    order_by: List[str]
    limit: int
    notes: str


class SQLPlanningAgent:
    async def run(self, intent_json: Dict[str, Any], schema_compact: str, max_rows: int) -> SQLPlan:
        llm = get_llm()
        system = (
            "You are a SQL planner. Create a query plan using only tables/columns from the schema hints. "
            "Prefer simple join paths using FK relationships. Return ONLY JSON matching schema."
        )
        user = (
            f"Intent JSON: {intent_json}\n\n"
            f"Schema hints (compact):\n{schema_compact}\n\n"
            f"Constraints: limit <= {max_rows}."
        )
        res = await llm.complete_json(system=system, user=user, schema=PLAN_SCHEMA, temperature=0.0)
        return SQLPlan(**(res.json or {}))