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
        st.subheader("Chart")
        import plotly.graph_objects as go
        import json
        import plotly.io as pio

        # chart_spec is a dict, convert to JSON string for from_json
        chart_json = json.dumps(out["chart_spec"])
        fig = pio.from_json(chart_json)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Answer")
    st.write(out["answer"])

    st.subheader("Insights")
    for i in out["insights"]:
        st.write(f"- {i}")

    st.subheader("Recommended next questions")
    for r in out["recommendations"]:
        st.write(f"- {r}")

    st.caption(f"Audit ID: {out['audit_id']}")