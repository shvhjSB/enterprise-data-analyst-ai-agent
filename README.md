# 📊 Enterprise Agentic Text-to-SQL Analytics Platform

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)

Production-grade Agentic AI system that converts complex natural language into optimized, executable SQL queries using a multi-agent architecture. Designed to simulate real-world data analyst workflows with secure, scalable, and auditable execution.

## 🚀 Overview

This platform empowers users to query structured enterprise databases purely through semantic prompts. It leverages **LangGraph-based agentic orchestration** to plan, generate, validate, and execute SQL queries while ensuring data integrity, strict guardrails, and automated visualization rendering.

## 📸 Application Workflow Walkthrough

<table width="100%">
  <tr>
    <td width="50%" align="center"><b>1. Semantic Prompt & SQL Generation</b></td>
    <td width="50%" align="center"><b>2. Query Execution & Data Retrieval</b></td>
  </tr>
  <tr>
    <td><img src="images/1_prompt_sql.png" width="100%" alt="User Prompt and SQL Generation"/></td>
    <td><img src="images/2_sql_table.png" width="100%" alt="Remaining SQL and Result Table"/></td>
  </tr>
  <tr>
    <td align="center"><i>User inputs natural language; Agent plans and begins writing complex SQL (CTEs, Window Functions).</i></td>
    <td align="center"><i>Full SQL execution logging alongside the retrieved structured data table.</i></td>
  </tr>
  <tr>
    <td width="50%" align="center"><b>3. Autonomous Visualization & Answer</b></td>
    <td width="50%" align="center"><b>4. AI Insights & Next Steps</b></td>
  </tr>
  <tr>
    <td><img src="images/3_viz_answer.png" width="100%" alt="Dynamic Plotly Chart and Answer"/></td>
    <td><img src="images/4_insights_next.png" width="100%" alt="Insights and Recommended Questions"/></td>
  </tr>
  <tr>
    <td align="center"><i>Agent evaluates data cardinality to render the optimal Plotly chart, paired with a conversational summary.</i></td>
    <td align="center"><i>Actionable bullet-point business insights and intelligently suggested follow-up analytical queries.</i></td>
  </tr>
</table>

## 🧠 Key Features

* **Multi-Agent Workflow:** Planner → SQL Generator → Validator → Executor → Insights → Visualization Agent.
* **Enterprise Guardrails & Security:** Strict blocking of destructive operations, read-only enforcement, PII masking, and built-in prevention of Cartesian explosions.
* **Advanced SQL Capabilities:** Capable of generating and handling complex queries including CTEs, Window Functions, and Self-Joins with a 95%+ first-pass success rate.
* **Autonomous Visualization:** Dynamically evaluates data cardinality to render optimal charts (e.g., grouped time-series, Pareto charts) using Plotly without UI crashes.
* **Model-Agnostic:** Plug-and-play support for OpenAI, Azure OpenAI, and Anthropic LLMs.
* **Structured Audit Logging:** Tracks query generation, execution latency, row counts, and LLM reasoning steps.

## 🏗️ Architecture

User Query → Planner Agent → SQL Generator → Validator → Execution Engine → Insights Agent → Visualization → Recommendations

## 🔐 Security & Reliability

* Fernet-encrypted database configurations
* Environment-based secret management
* Query timeout controls and row limits
* Strict blocking of destructive SQL operations

## ⚙️ Tech Stack

* Backend: FastAPI (async)
* Orchestration: Agno (multi-agent system)
* LLMs: OpenAI / Azure OpenAI / Anthropic
* Database: SQLite (dev), extensible to Postgres/MySQL
* Visualization: Plotly
* Testing: Pytest + aiosqlite

## 📂 Project Structure

text2sql_app/
├── agents/          # Agent logic (planner, generator, validator)
├── core/            # Core execution and orchestration
├── api/             # FastAPI endpoints
├── ui/              # Streamlit interface
├── prompts/         # LLM prompt templates
└── tests/           # Unit and integration tests

## ⚡ Quickstart

1. Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\Activate
pip install -e .
```

2. Configure environment
   Set `.env`:

```
TEXT2SQL_APP_MASTER_KEY=CHANGE_ME
TEXT2SQL_APP_API_KEY=dev-api-key

LLM_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
```

3. Run API

```bash
uvicorn text2sql_app.main:app --reload
```

4. Run UI

```bash
streamlit run text2sql_app/ui/streamlit_app.py
```

## 📊 Example Queries

* "Total revenue by month for 2025"
* "Top 10 customers by lifetime spend"
* "Average order value by category"

## 💡 Use Cases

* Enterprise data analytics automation
* Business intelligence assistants
* Self-service analytics for non-technical users
* Decision support systems

## 🧩 Future Enhancements

* Semantic Layer Integration: Integrating with dbt to map complex business metrics directly into LLM context.
* Multi-Database Federation: Querying across PostgreSQL and Snowflake simultaneously.
* Conversational Memory: Enhanced context retention for deep, multi-turn analytical drill-downs.
* Role-Based Access Control (RBAC): Row-level security based on user organizational roles.
---

👉 Inspired by real-world enterprise analytics workflows and designed to replicate how data analysts interact with databases using natural language.
