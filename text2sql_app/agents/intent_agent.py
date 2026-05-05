"""Business Intent Understanding Agent.

Produces a structured JSON intent from a natural language question.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from text2sql_app.core.llm import get_llm


INTENT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "business_intent": {"type": "string"},
        "metrics": {"type": "array", "items": {"type": "string"}},
        "dimensions": {"type": "array", "items": {"type": "string"}},
        "filters": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "field": {"type": "string"},
                    "op": {"type": "string"},
                    "value": {"type": ["string", "number", "boolean", "null"]},
                },
                "required": ["field", "op", "value"],
            },
        },
        "time_range": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "start": {"type": ["string", "null"]},
                "end": {"type": ["string", "null"]},
                "granularity": {"type": ["string", "null"]},
            },
            "required": ["start", "end", "granularity"],
        },
        "confidence": {"type": "number"},
        "notes": {"type": "string"},
    },
    "required": ["business_intent", "metrics", "dimensions", "filters", "time_range", "confidence", "notes"],
}


@dataclass
class Intent:
    business_intent: str
    metrics: List[str]
    dimensions: List[str]
    filters: List[Dict[str, Any]]
    time_range: Dict[str, Any]
    confidence: float
    notes: str


class BusinessIntentAgent:
    async def run(self, question: str, schema_compact: str) -> Intent:
        llm = get_llm()
        system = (
            "You are a Business Intent Analyst for enterprise analytics. "
            "Return ONLY valid JSON matching the provided schema. "
            "Do not invent tables/columns; refer to schema hints if needed."
        )
        user = (
            f"Question: {question}\n\n"
            f"Schema hints (compact):\n{schema_compact}\n\n"
            "Extract business intent, metrics, dimensions, filters, and time range. "
            "If unclear, keep confidence low and describe ambiguity in notes."
        )
        res = await llm.complete_json(system=system, user=user, schema=INTENT_SCHEMA, temperature=0.0)
        obj = res.json or {}
        return Intent(**obj)