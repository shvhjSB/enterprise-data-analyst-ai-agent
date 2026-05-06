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
    async def run(self, plan_json: Dict[str, Any], intent_json: Dict[str, Any], schema_compact: str, dialect: str) -> SQLDraft:
        llm = get_llm()
        system = (
            "You are an Expert SQL Developer. Generate precise SQL. "
            "You MUST strictly follow the provided CTE Execution Plan. "
            "CRITICAL RULE FOR WINDOW FUNCTIONS: Never JOIN a base table to a CTE that only contains Window Functions (like SUM() OVER()) without a GROUP BY or DISTINCT. This causes Cartesian Explosion/Fan-out. Instead, calculate Window Functions directly in the SELECT clause of your aggregated base CTE."
            "Return ONLY JSON."
        )
        user = (
            f"DB dialect: {dialect}\n\n"
            f"Query Type: {intent_json.get('query_type')}\n"
            f"Execution Plan: {plan_json.get('cte_steps')}\n\n"
            f"Schema hints:\n{schema_compact}\n\n"
            "--- SYNTAX RULES ---\n"
            "- NEVER put window functions (like ROW_NUMBER) in a HAVING or WHERE clause directly. ALWAYS put them in a CTE or Subquery first, then filter in the outer query.\n"
            "- Ensure all column references in JOINs are fully qualified (e.g., table_name.column_name) to avoid ambiguity.\n"
            "--------------------\n\n"
            "Output the final SQL and a brief explanation."
        )
        res = await llm.complete_json(system=system, user=user, schema=SQL_SCHEMA, temperature=0.0)
        obj = res.json or {}
        return SQLDraft(sql=obj["sql"], explanation=obj["explanation"])