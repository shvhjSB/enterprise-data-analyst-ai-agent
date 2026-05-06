from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List
from text2sql_app.core.llm import get_llm

INTENT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "reasoning": {"type": "string", "description": "Explain the core user intent. Resolve ambiguities: e.g., 'highest' vs 'Top N', 'value' vs 'growth', 'snapshot' vs 'trend'."},
        "query_type": {
            "type": "string", 
            "enum": ["snapshot", "ranking", "time_series_trend", "period_over_period_growth", "percentage_contribution"],
            "description": "Strictly classify the type of query."
        },
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
    "required": ["reasoning", "query_type", "business_intent", "metrics", "dimensions", "filters", "time_range", "confidence", "notes"],
}

@dataclass
class Intent:
    reasoning: str
    query_type: str
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
            "Think step-by-step in the 'reasoning' field before classifying."
        )
        user = (
            f"Schema hints:\n{schema_compact}\n\n"
            "--- EXAMPLES ---\n"
            "Q: 'What is the MoM revenue growth?'\n"
            "A: {\"reasoning\": \"User is asking for Month-over-Month comparison.\", \"query_type\": \"period_over_period_growth\"}\n\n"
            
            "Q: 'Show me the top 3 selling products in each region.'\n"
            "A: {\"reasoning\": \"Ranking items within groups (regions).\", \"query_type\": \"ranking\"}\n\n"
            
            "Q: 'What share of total sales comes from enterprise clients?'\n"
            "A: {\"reasoning\": \"User wants a proportion or percentage of the whole.\", \"query_type\": \"percentage_contribution\"}\n"
            "----------------\n\n"
            
            f"Question: {question}\n"
            "Extract business intent, metrics, and strictly classify the query_type."
        )
        res = await llm.complete_json(system=system, user=user, schema=INTENT_SCHEMA, temperature=0.0)
        obj = res.json or {}
        return Intent(**obj)