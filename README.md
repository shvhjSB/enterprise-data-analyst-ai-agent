# Enterprise Agentic Text-to-SQL Analytics Platform

Production-grade Agentic AI system that converts natural language into optimized SQL queries using a multi-agent architecture. Designed to simulate real-world data analyst workflows with secure, scalable, and auditable execution.

## 🚀 Overview

This platform enables users to query structured databases using natural language. It leverages agentic orchestration to plan, generate, validate, and execute SQL queries while ensuring safety, accuracy, and interpretability.

## 🧠 Key Features

* Multi-agent workflow: Planner → SQL Generator → Validator → Executor → Insights → Visualization
* Secure query execution with read-only enforcement, PII guardrails, and query limits
* Schema-aware SQL generation for higher accuracy
* Automatic error correction and retry mechanisms
* Structured audit logging (queries, latency, errors, row counts)
* Model-agnostic LLM support (OpenAI, Azure OpenAI, Anthropic)
* Interactive visualization support using Plotly

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
source .venv/bin/activate
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

* LangGraph-based agent orchestration
* Multi-database federation
* Conversational memory for follow-up queries
* Role-based access control (RBAC)

---

👉 Inspired by real-world enterprise analytics workflows and designed to replicate how data analysts interact with databases using natural language.
