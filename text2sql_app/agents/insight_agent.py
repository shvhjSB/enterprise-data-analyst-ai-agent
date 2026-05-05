"""Insight & Explanation Agent.

Converts raw results into a natural-language answer and insights.
Must not hallucinate beyond returned data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from text2sql_app.core.llm import get_llm


INSIGHT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "answer": {"type": "string"},
        "insights": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["answer", "insights"],
}


@dataclass
class Insight:
    answer: str
    insights: List[str]


class InsightAgent:
    async def run(self, question: str, sql: str, columns: List[str], rows: List[List[Any]]) -> Insight:
        llm = get_llm()
        system = (
            "You are an analytics explainer. Use ONLY the provided result rows. "
            "If data is insufficient, say so clearly. Return ONLY JSON."
        )
        user = (
            f"Question: {question}\n"
            f"SQL: {sql}\n\n"
            f"Columns: {columns}\n"
            f"Rows (truncated): {rows[:50]}\n\n"
            "Write a concise business answer and 3-6 bullet insights."
        )
        res = await llm.complete_json(system=system, user=user, schema=INSIGHT_SCHEMA, temperature=0.2)
        obj = res.json or {}
        return Insight(answer=obj["answer"], insights=obj["insights"])