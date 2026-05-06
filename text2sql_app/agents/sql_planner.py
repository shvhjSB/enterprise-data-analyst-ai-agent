from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List
from text2sql_app.core.llm import get_llm

PLAN_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "query_strategy": {
            "type": "string", 
            "description": "Explain if window functions (LAG, SUM OVER), or multiple CTEs are needed based on the query type."
        },
        "cte_steps": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "step_name": {"type": "string"},
                    "description": {"type": "string", "description": "What this step does (e.g., aggregate base data, calculate lag, final rank)"},
                    "requires_window_function": {"type": "boolean"}
                },
                "required": ["step_name", "description", "requires_window_function"]
            }
        },
        "tables": {"type": "array", "items": {"type": "string"}},
        "limit": {"type": "integer"},
        "notes": {"type": "string"}
    },
    "required": ["query_strategy", "cte_steps", "tables", "limit", "notes"],
}

@dataclass
class SQLPlan:
    query_strategy: str
    cte_steps: List[Dict[str, Any]]
    tables: List[str]
    limit: int
    notes: str

class SQLPlanningAgent:
    async def run(self, intent_json: Dict[str, Any], schema_compact: str, max_rows: int) -> SQLPlan:
        llm = get_llm()
        system = (
            "You are a SQL Data Architect. Create a step-by-step query execution plan using CTEs. "
            "Return ONLY JSON matching the schema."
        )
        user = (
            f"Intent JSON: {intent_json}\n\n"
            f"Schema hints:\n{schema_compact}\n\n"
            "--- EXAMPLES ---\n"
            "Scenario: query_type is 'ranking' and user wants top N per category.\n"
            "Plan Strategy: \"Requires window function. Step 1: Base data aggregation. Step 2: Calculate ROW_NUMBER() OVER(PARTITION BY category ORDER BY metric DESC). Step 3: Filter where rn <= N.\"\n\n"
            
            "Scenario: query_type is 'percentage_contribution'.\n"
            "Plan Strategy: \"Requires window function. Step 1: Calculate raw metric per dimension. Step 2: Calculate SUM(metric) OVER() to get grand total. Step 3: Divide row metric by grand total.\"\n\n"
            
            "Scenario: query_type is 'period_over_period_growth'.\n"
            "Plan Strategy: \"Requires window function. Step 1: Aggregate metric by time period. Step 2: Use LAG(metric) OVER(ORDER BY time) to get previous period. Step 3: Calculate (current - previous) / previous.\"\n"
            "----------------\n\n"
            
            f"Constraints: limit <= {max_rows}. "
            "Plan the necessary CTEs and flag window functions."
        )
        res = await llm.complete_json(system=system, user=user, schema=PLAN_SCHEMA, temperature=0.0)
        plan = SQLPlan(**(res.json or {}))
        return plan