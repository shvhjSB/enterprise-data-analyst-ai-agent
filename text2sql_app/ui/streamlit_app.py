"""Streamlit demo UI.

FastAPI remains UI-agnostic; this is a simple reference client.
"""

from __future__ import annotations

import os
import requests
import streamlit as st


API_URL = os.getenv("TEXT2SQL_API_URL", "http://localhost:8000")
API_KEY = os.getenv("TEXT2SQL_APP_API_KEY", "dev-api-key")


def _post(path: str, payload: dict):
    r = requests.post(
        f"{API_URL}{path}",
        json=payload,
        headers={"X-API-Key": API_KEY},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


st.title("Text-to-SQL Analytics Platform")

with st.sidebar:
    st.header("DB Connection")
    db_id = st.text_input("DB ID", value="local")
    db_url = st.text_input("DB URL", value="sqlite+aiosqlite:///./example.db")

    if st.button("Connect"):
        resp = _post("/connect-db", {"db_id": db_id, "db_url": db_url, "schema": None})
        st.success(f"Connected: {resp}")

    if st.button("Introspect"):
        resp = _post("/introspect", {"db_id": db_id})
        st.success(resp)

st.header("Ask a question")
question = st.text_area("Natural language question", value="Total revenue by month")

if st.button("Run"):
    out = _post("/ask", {"db_id": db_id, "question": question})

    st.subheader("Generated SQL")
    st.code(out["sql"], language="sql")

    st.subheader("Result")
    st.dataframe(out["result"]["rows"], width="stretch")

    if out.get("chart_spec"):
        st.subheader("Visualization")
        chart_spec = out["chart_spec"]
        
        # 1. Agar chart_type "kpi_card" hai
        if chart_spec.get("type") == "kpi_card":
            st.metric(label=chart_spec.get("title", "Key Metric"), value=chart_spec.get("value"))
            
        # 2. Plotly Charts
        else:
            import plotly.express as px
            import pandas as pd
            
            df_data = {}
            x_col = chart_spec.get("x_label") or "X"
            y_col = chart_spec.get("y_label") or "Y"
            
            if "x" in chart_spec: df_data[x_col] = chart_spec["x"]
            if "y" in chart_spec: df_data[y_col] = chart_spec["y"]
            
            color_col = None
            if "color" in chart_spec and chart_spec["color"]:
                color_col = chart_spec.get("color_label") or "Color"
                df_data[color_col] = chart_spec["color"]
                
            df_viz = pd.DataFrame(df_data)
            title = chart_spec.get("title", "")
            c_type = chart_spec.get("type")
            
            try:
                # Dynamic Chart Rendering
                if c_type == "horizontal_bar":
                    # Y-axis ko strictly String (Category) bana do, taaki Plotly numbers dekh kar confuse na ho
                    df_viz[y_col] = df_viz[y_col].astype(str)
                    
                    # Yahan fix kiya hai: AI ne X ko value aur Y ko category rakha hai, toh x=x_col hi rahega
                    fig = px.bar(df_viz, x=x_col, y=y_col, color=color_col, orientation='h', title=title)
                    fig.update_layout(yaxis={'categoryorder':'total ascending'})
                    fig.update_yaxes(type='category')
                    
                elif c_type == "line":
                    fig = px.line(df_viz, x=x_col, y=y_col, color=color_col, title=title)
                elif c_type == "pie":
                    fig = px.pie(df_viz, names=x_col, values=y_col, title=title)
                elif c_type == "donut":
                    fig = px.pie(df_viz, names=x_col, values=y_col, hole=0.4, title=title)
                elif c_type == "scatter":
                    fig = px.scatter(df_viz, x=x_col, y=y_col, color=color_col, title=title)
                else: 
                    # Auto-Fallback Check: Agar normal bar hai aur label bohot lamba hai, toh UI khud horizontal karega
                    if df_viz[x_col].dtype == 'object' and df_viz[x_col].astype(str).str.len().max() > 15:
                        df_viz[x_col] = df_viz[x_col].astype(str)
                        # Yahan override ho raha hai, isliye x=y_col hoga
                        fig = px.bar(df_viz, x=y_col, y=x_col, color=color_col, orientation='h', title=title)
                        fig.update_layout(yaxis={'categoryorder':'total ascending'})
                    else:
                        # Ensure categorical axis for numeric IDs on standard bar
                        if x_col in df_viz.columns and pd.api.types.is_numeric_dtype(df_viz[x_col]) and df_viz[x_col].nunique() < 20:
                            df_viz[x_col] = df_viz[x_col].astype(str)
                        fig = px.bar(df_viz, x=x_col, y=y_col, color=color_col, title=title)
                
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not render the chart perfectly. Error: {e}")

    st.subheader("Answer")
    st.write(out["answer"])

    st.subheader("Insights")
    for i in out["insights"]:
        st.write(f"- {i}")

    st.subheader("Recommended next questions")
    for r in out["recommendations"]:
        st.write(f"- {r}")

    st.caption(f"Audit ID: {out['audit_id']}")