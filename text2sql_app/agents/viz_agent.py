"""Visualization Agent.

Outputs a Plotly figure JSON spec when the result is chartable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from text2sql_app.core.llm import get_llm


VIZ_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "chartable": {"type": "boolean"},
        "chart_type": {"type": ["string", "null"]},
        "x": {"type": ["string", "null"]},
        "y": {"type": ["string", "null"]},
        "color": {"type": ["string", "null"]},
        "title": {"type": "string"},
    },
    "required": ["chartable", "chart_type", "x", "y", "color", "title"],
}


@dataclass
class VizDecision:
    chartable: bool
    chart_type: str | None
    x: str | None
    y: str | None
    color: str | None
    title: str


class VisualizationAgent:
    async def decide(self, question: str, columns: List[str], rows: List[List[Any]]) -> VizDecision:
        llm = get_llm()
        system = "You are a data visualization expert. Decide a sensible chart mapping. Return ONLY JSON."
        user = (
            f"Question: {question}\n"
            f"Columns: {columns}\n"
            f"Sample rows: {rows[:25]}\n\n"
            "Choose bar/line/scatter/pie/histogram if appropriate."
        )
        res = await llm.complete_json(system=system, user=user, schema=VIZ_SCHEMA, temperature=0.0)
        return VizDecision(**(res.json or {}))

    def to_plotly_spec(self, decision: VizDecision, columns: List[str], rows: List[List[Any]]) -> Optional[Dict[str, Any]]:
        if not decision.chartable or not decision.x or not decision.y:
            return None

        # Build a simple Plotly Express-like spec without importing plotly.express.
        # Frontend can render via plotly.io.from_json.
        x_idx = columns.index(decision.x) if decision.x in columns else 0
        y_idx = columns.index(decision.y) if decision.y in columns else 1

        x_vals = [r[x_idx] for r in rows]
        y_vals = [r[y_idx] for r in rows]

        chart_type = (decision.chart_type or "bar").lower()
        trace: Dict[str, Any]
        if chart_type == "line":
            trace = {"type": "scatter", "mode": "lines+markers", "x": x_vals, "y": y_vals}
        elif chart_type == "scatter":
            trace = {"type": "scatter", "mode": "markers", "x": x_vals, "y": y_vals}
        elif chart_type == "histogram":
            trace = {"type": "histogram", "x": y_vals}
        else:
            trace = {"type": "bar", "x": x_vals, "y": y_vals}

        fig = {
            "data": [trace],
            "layout": {"title": {"text": decision.title}, "xaxis": {"title": decision.x}, "yaxis": {"title": decision.y}},
        }
        return fig