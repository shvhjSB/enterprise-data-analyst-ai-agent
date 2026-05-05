# Text-to-SQL Analytics Platform (Enterprise-ready)

Production-grade, modular Text-to-SQL analytics backend with agentic orchestration (Agno), secure schema introspection, SQL planning/generation/validation, safe execution, NL insights, and Plotly chart specs.

## Key Features
- **FastAPI (async)**, UI-agnostic APIs
- **Agno multi-agent orchestration** with structured intent → plan → SQL → validation → execution → insights → visualization → recommendations
- **Secure DB config**: Fernet-encrypted configs on disk; secrets via env
- **SQL safety**: read-only enforcement, destructive statement blocking, row limits, timeouts, PII guardrails
- **Auditable**: structured audit logs (question, SQL, timings, row counts, errors)
- **Model-agnostic LLM**: provider interface + OpenAI/Azure OpenAI/Anthropic stubs
- **Local validation**: SQLite for examples + tests (async aiosqlite)

## Project Structure
```text
text2sql_app/
├── agents/
├── core/
├── api/
├── ui/
├── prompts/
└── tests/
```

## Quickstart
### 1) Create venv
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2) Configure environment
Create `.env` (or export env vars):
```bash
# Security
TEXT2SQL_APP_MASTER_KEY=CHANGE_ME_32+_BYTES_BASE64_OR_HEX
TEXT2SQL_APP_API_KEY=dev-api-key

# LLM (choose one provider)
LLM_PROVIDER=openai  # openai|azure_openai|anthropic
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini

# Optional
TEXT2SQL_APP_DATA_DIR=.data
TEXT2SQL_APP_MAX_ROWS=5000
TEXT2SQL_APP_QUERY_TIMEOUT_SECONDS=30
```

### 3) Run API
```bash
uvicorn text2sql_app.main:app --reload
```

### 4) Run Streamlit demo
```bash
streamlit run text2sql_app/ui/streamlit_app.py
```

## Example flow
1. `POST /connect-db` with a SQLite URL, e.g. `sqlite+aiosqlite:///./example.db`
2. `POST /introspect` to build schema cache
3. `POST /ask` with natural language question

## Example questions
- "Total revenue by month for 2025"
- "Top 10 customers by lifetime spend"
- "What is the average order value by product category?"

## Notes
- This repo defaults to **SQLite** for local development. Other DBs (Postgres/MySQL/etc.) are supported via SQLAlchemy async drivers.
- Store credentials in environment variables; encrypted configs contain connection URLs only.