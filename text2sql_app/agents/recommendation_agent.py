"""Recommendation Agent.

Suggests follow-up questions and actions. Must label as recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from text2sql_app.core.llm import get_llm


REC_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "recommendations": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["recommendations"],
}


@dataclass
class Recommendations:
    recommendations: List[str]


class RecommendationAgent:
    async def run(self, question: str, answer: str, columns: List[str]) -> Recommendations:
        llm = get_llm()
        system = (
            "You are a business analyst. Propose follow-up questions and actions as recommendations. "
            "Do not state recommendations as facts. Return ONLY JSON."
        )
        user = (
            f"Original question: {question}\n"
            f"Answer summary: {answer}\n"
            f"Available columns: {columns}\n\n"
            "Return 3-6 recommended next questions." 
        )
        res = await llm.complete_json(system=system, user=user, schema=REC_SCHEMA, temperature=0.4)
        return Recommendations(**(res.json or {}))