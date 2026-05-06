from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List
from text2sql_app.core.llm import get_llm
from typing import Optional

VIZ_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "reasoning": {
            "type": "string", 
            "description": "Explain WHY this chart makes human sense based on the query intent, data distribution, and cardinality."
        },
        "chart_type": {
            "type": "string",
            "enum": ["line", "bar", "horizontal_bar", "pie", "donut", "scatter", "kpi_card", "table_only"],
            "description": "The visual format. Use kpi_card for single metrics. Use horizontal_bar for rankings. Use line for time-series."
        },
        "x": {"type": ["string", "null"], "description": "The dimension or temporal column. NEVER a numeric metric unless it's a scatter plot."},
        "y": {"type": ["string", "null"], "description": "The primary numeric metric column."},
        "color": {"type": ["string", "null"], "description": "A categorical dimension for grouping. MUST have low cardinality (< 10 unique values)."},
        "title": {"type": "string"}
    },
    "required": ["reasoning", "chart_type", "x", "y", "color", "title"],
}

@dataclass
class VizDecision:
    reasoning: str
    chart_type: str
    x: str | None
    y: str | None
    color: str | None
    title: str

class VisualizationAgent:
    async def decide(self, intent_json: Dict[str, Any], question: str, columns: List[str], rows: List[List[Any]]) -> VizDecision:
        llm = get_llm()
        query_type = intent_json.get("query_type", "snapshot")
        
        # Pre-calculate data shape to feed into the prompt
        row_count = len(rows)
        col_count = len(columns)
        is_single_value = row_count == 1 and col_count == 1
        
        # Sample unique values for potential color columns to prevent spaghetti charts
        cardinality_hints = []
        if row_count > 0:
            for i, col in enumerate(columns):
                unique_vals = set([str(r[i]) for r in rows if r[i] is not None])
                if len(unique_vals) <= 15:
                    cardinality_hints.append(f"Column '{col}' has {len(unique_vals)} unique values (Safe for Color/Grouping).")
                else:
                    cardinality_hints.append(f"Column '{col}' has {len(unique_vals)} unique values (HIGH CARDINALITY - DO NOT USE FOR COLOR).")

        system = (
            "You are an Expert Enterprise BI Architect. Your job is to select the most semantic, readable visualization for a dataset. "
            "CRITICAL PLOTLY RULE: Whenever the dataset contains a categorical column (like 'country', 'product_name', 'customer_id') alongside a time-series or numerical X-axis, you MUST explicitly group the lines by setting the color parameter in Plotly (e.g., px.line(df, x='month', y='cumulative_revenue', color='country')). NEVER plot multiple entities without the color parameter, otherwise Plotly will draw one giant, zig-zagging broken line."
            "RULE: If the result data contains exactly 1 row and 1 numeric column (a single scalar value like total revenue, count, or average), DO NOT generate a chart. Instead, return a 'KPI' or 'Table_Only' format."
            "Return ONLY JSON matching the schema."
        )
        
        user = (
            f"Question: {question}\n"
            f"Query Intent: {query_type}\n"
            f"Columns: {columns}\n"
            f"Data Shape: {row_count} rows, {col_count} columns\n"
            f"Cardinality Profile:\n" + "\n".join(cardinality_hints) + "\n\n"
            f"Sample rows: {rows[:5]}\n\n"
            "--- STRICT ENTERPRISE BI RULES ---\n"
            "1. KPI / METRIC: If the data is just 1 row and 1 column (e.g., total revenue), choose 'kpi_card'. DO NOT attempt to chart it.\n"
            "2. TEMPORAL TRENDS: If intent is 'time_series_trend' or 'period_over_period_growth', MUST use 'line' or 'bar'. 'x' MUST be the date/time column.\n"
            "3. RANKING / PARETO: If intent is 'ranking', prefer 'horizontal_bar' for readability, especially if dimension names are long. 'y' is the dimension, 'x' is the metric.\n"
            "4. PROPORTION: If intent is 'percentage_contribution', use 'donut' or 'pie' ONLY IF rows <= 7. Otherwise, use 'bar' or 'table_only'.\n"
            "5. CARDINALITY / SPAGHETTI CHART PREVENTION: NEVER use a column for 'color' if it has high cardinality (>10). If the chart will be unreadable, fallback to 'table_only'.\n"
            "6. SEMANTICS: 'x' is almost always a dimension (string/date). 'y' is almost always a metric (number). Never map a metric ID or raw number to a legend/color.\n"
        )
        
        res = await llm.complete_json(system=system, user=user, schema=VIZ_SCHEMA, temperature=0.0)
        decision = VizDecision(**(res.json or {}))
        
        # Guardrail: Force KPI if data is literally one number
        if is_single_value:
            decision.chart_type = "kpi_card"
            decision.x = None
            decision.y = None
            decision.color = None

        return decision

    def to_plotly_spec(self, decision: VizDecision, columns: List[str], rows: List[List[Any]]) -> Optional[Dict[str, Any]]:
        # Agar table_only hai, toh None return karo (UI bas table dikhayega)
        if decision.chart_type == "table_only":
            return None
            
        # Agar KPI Card hai, toh value bhej do
        if decision.chart_type == "kpi_card":
            return {
                "type": "kpi_card",
                "title": decision.title,
                "value": rows[0][0] if rows and rows[0] else "N/A"
            }

        # Standard safety checks for other charts
        if not decision.x or not decision.y:
            return None
        if decision.x not in columns or decision.y not in columns:
            return None

        x_idx = columns.index(decision.x)
        y_idx = columns.index(decision.y)
        
        x_vals = [r[x_idx] for r in rows if len(r) > max(x_idx, y_idx)]
        y_vals = [r[y_idx] for r in rows if len(r) > max(x_idx, y_idx)]

        if decision.chart_type == "line":
            try:
                sorted_pairs = sorted(zip(x_vals, y_vals))
                x_vals = [p[0] for p in sorted_pairs]
                y_vals = [p[1] for p in sorted_pairs]
            except Exception:
                pass 

        color_vals = None
        if decision.color and decision.color in columns:
            c_idx = columns.index(decision.color)
            color_vals = [r[c_idx] for r in rows if len(r) > c_idx]

        spec = {
            "type": decision.chart_type,
            "x": x_vals,
            "y": y_vals,
            "title": decision.title,
            "x_label": decision.x,
            "y_label": decision.y
        }
        
        if color_vals:
            spec["color"] = color_vals
            spec["color_label"] = decision.color

        return spec