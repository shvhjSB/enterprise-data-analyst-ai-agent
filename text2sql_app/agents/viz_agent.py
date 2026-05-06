"""Visualization Agent.

Outputs a Plotly figure JSON spec when the result is chartable.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from text2sql_app.core.llm import get_llm

# Keep VIZ_SCHEMA as you have it...
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
    # Update method signature to accept intent
    async def decide(self, intent_json: Dict[str, Any], question: str, columns: List[str], rows: List[List[Any]]) -> VizDecision:
        llm = get_llm()
        query_type = intent_json.get("query_type", "snapshot")
        
        system = "You are a data visualization expert. Return ONLY JSON."
        user = (
            f"Query Type: {query_type}\n"
            f"Question: {question}\n"
            f"Columns: {columns}\n"
            f"Sample rows: {rows[:25]}\n\n"
            "Rules:\n"
            "1. If Query Type is 'time_series_trend' or 'period_over_period_growth', you MUST use 'line' or 'bar', and 'x' MUST be the time column.\n"
            "2. If Query Type is 'percentage_contribution', prefer 'pie' or 'bar'.\n"
            "3. If data is insufficient or illogical to chart, set chartable to false."
        )
        res = await llm.complete_json(system=system, user=user, schema=VIZ_SCHEMA, temperature=0.0)
        decision = VizDecision(**(res.json or {}))

        if decision.chartable and not decision.color and len(columns) >= 3:
            decision.color = columns[1]

        return decision
        

    def to_plotly_spec(self, decision: VizDecision, columns: List[str], rows: List[List[Any]]) -> Optional[Dict[str, Any]]:
        if not decision.chartable or not decision.x or not decision.y:
            return None

        if not rows or len(columns) < 2:
            return None

        x_idx = columns.index(decision.x) if decision.x in columns else 0
        y_idx = columns.index(decision.y) if decision.y in columns else 1

        if x_idx >= len(columns) or y_idx >= len(columns):
            return None

        x_vals = [r[x_idx] for r in rows if len(r) > max(x_idx, y_idx)]
        y_vals = [r[y_idx] for r in rows if len(r) > max(x_idx, y_idx)]

        chart_type = (decision.chart_type or "bar").lower()

        # 🔥 STEP 3: GROUPED CHART LOGIC
        color_idx = None
        if decision.color and decision.color in columns:
            color_idx = columns.index(decision.color)

        if color_idx is not None:
            categories = list(set(r[color_idx] for r in rows if len(r) > color_idx))
            traces = []

            for cat in categories:
                x_sub = [r[x_idx] for r in rows if len(r) > max(x_idx, y_idx, color_idx) and r[color_idx] == cat]
                y_sub = [r[y_idx] for r in rows if len(r) > max(x_idx, y_idx, color_idx) and r[color_idx] == cat]

                if chart_type == "line":
                    trace = {
                        "type": "scatter",
                        "mode": "lines+markers",
                        "name": str(cat),
                        "x": x_sub,
                        "y": y_sub
                    }
                elif chart_type == "scatter":
                    trace = {
                        "type": "scatter",
                        "mode": "markers",
                        "name": str(cat),
                        "x": x_sub,
                        "y": y_sub
                    }
                else:
                    trace = {
                        "type": "bar",
                        "name": str(cat),
                        "x": x_sub,
                        "y": y_sub
                    }

                traces.append(trace)

            data = traces

        else:
            if chart_type == "line":
                data = [{"type": "scatter", "mode": "lines+markers", "x": x_vals, "y": y_vals}]
            elif chart_type == "scatter":
                data = [{"type": "scatter", "mode": "markers", "x": x_vals, "y": y_vals}]
            elif chart_type == "histogram":
                data = [{"type": "histogram", "x": y_vals}]
            else:
                data = [{"type": "bar", "x": x_vals, "y": y_vals}]

        fig = {
            "data": data,
            "layout": {
                "title": {"text": decision.title},
                "xaxis": {"title": decision.x},
                "yaxis": {"title": decision.y},
                "barmode": "group"
            },
        }

        return fig