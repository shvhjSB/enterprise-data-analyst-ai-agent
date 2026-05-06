"""Orchestrator for Text2SQL analytics pipeline."""

from __future__ import annotations

import uuid

from text2sql_app.agents.execution_agent import ExecutionAgent
from text2sql_app.agents.insight_agent import InsightAgent
from text2sql_app.agents.intent_agent import BusinessIntentAgent
from text2sql_app.agents.recommendation_agent import RecommendationAgent
from text2sql_app.agents.schema_agent import SchemaIntelligenceAgent
from text2sql_app.agents.sql_generator import SQLGenerationAgent
from text2sql_app.agents.sql_planner import SQLPlanningAgent
from text2sql_app.agents.sql_validator import SQLValidationAgent
from text2sql_app.agents.viz_agent import VisualizationAgent
from text2sql_app.api.schemas import AskResponse, QueryResult
from text2sql_app.core.config import get_settings
from text2sql_app.core.logging import audit_log
from text2sql_app.core.security import detect_pii_columns
from text2sql_app.core.llm import get_llm
from text2sql_app.services.connection_service import ConnectionService


# ---------------- HELPER FUNCTIONS ---------------- #

def _compact_schema(snapshot) -> str:
    """Compacts the schema snapshot to save LLM context window space."""
    lines = []
    for t in snapshot.tables:
        cols = ", ".join([f"{c.name}:{c.type}" for c in t.columns][:30])
        fks = ", ".join([f"{fk.column}->{fk.referred_table}.{fk.referred_column}" for fk in t.foreign_keys][:20])
        lines.append(
            f"TABLE {t.name} (fact={t.is_fact}, dim={t.is_dimension}) cols=[{cols}] fks=[{fks}]"
        )
    return "\n".join(lines)


# ---------------- MAIN ORCHESTRATOR ---------------- #

class Orchestrator:
    async def answer_question(self, db_id: str, question: str) -> AskResponse:
        settings = get_settings()
        audit_id = str(uuid.uuid4())

        svc = ConnectionService()
        db_url = svc.get_db_url(db_id)
        schema = svc.load_cached_schema(db_id)
        schema_compact = _compact_schema(schema)

        blocked = detect_pii_columns([c.split(".")[-1] for c in schema.all_column_names()])

        audit_log(
            "question_received",
            {"audit_id": audit_id, "db_id": db_id, "question": question},
        )

        # Initialize Agents
        schema_agent = SchemaIntelligenceAgent()
        intent_agent = BusinessIntentAgent()
        planner = SQLPlanningAgent()
        generator = SQLGenerationAgent()
        validator = SQLValidationAgent()
        executor = ExecutionAgent()
        insight_agent = InsightAgent()
        viz_agent = VisualizationAgent()
        rec_agent = RecommendationAgent()

        # 1) Schema Introspection
        _ = await schema_agent.run(db_id)

        # 2) Intent Extraction (The Brains)
        intent = await intent_agent.run(question=question, schema_compact=schema_compact)

        # 3) SQL Planning (The Strategist)
        plan = await planner.run(
            intent_json=intent.__dict__,
            schema_compact=schema_compact,
            max_rows=settings.text2sql_app_max_rows
        )

        # 4) SQL Generation (The Builder)
        raw_dialect = db_url.split(":")[0]
        dialect = raw_dialect.split("+")[0] # Turns 'postgresql+psycopg2' into just 'postgresql'
        draft = await generator.run(
            plan_json=plan.__dict__,
            intent_json=intent.__dict__,
            schema_compact=schema_compact,
            dialect=dialect
        )
        sql = draft.sql

        # 5) Deterministic Validation (Guardrails)
        outcome = validator.run(
            sql,
            max_rows=settings.text2sql_app_max_rows,
            blocked_columns=blocked
        )

        if not outcome.ok:
            audit_log(
                "sql_rejected",
                {"audit_id": audit_id, "reason": outcome.reason, "sql": sql},
            )
            raise ValueError(f"Unsafe SQL rejected: {outcome.reason}")

        safe_sql = outcome.sql

        # 6) Execution & LLM Self-Correction Loop
        exec_res = None
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                exec_res = await executor.run(db_url=db_url, sql=safe_sql)
                break  # Execution succeeded, exit the retry loop
            
            except Exception as e:
                if attempt == max_retries - 1:
                    # If this was the last attempt, log and raise the error
                    audit_log(
                        "execution_failed",
                        {"audit_id": audit_id, "sql": safe_sql, "error": str(e)},
                    )
                    raise RuntimeError(f"Database execution failed after retries: {str(e)}")
                
                # Dynamic Self-Correction using the actual database error
                llm = get_llm()
                fix_prompt = (
                    f"The following SQL failed to execute on the database.\n"
                    f"SQL:\n{safe_sql}\n\n"
                    f"Database Error: {str(e)}\n\n"
                    "Fix the syntax or logic error and return ONLY the corrected SQL in JSON format: {'sql': '...'}"
                )
                
                res = await llm.complete_json(
                    system="You are a strict SQL correction expert.", 
                    user=fix_prompt, 
                    schema={
                        "type": "object", 
                        "additionalProperties": False,
                        "properties": {"sql": {"type": "string"}},
                        "required": ["sql"]
                    }, 
                    temperature=0.0
                )
                
                if res.json and "sql" in res.json:
                    safe_sql = res.json["sql"]
                    audit_log(
                        "sql_auto_corrected", 
                        {"audit_id": audit_id, "error": str(e), "new_sql": safe_sql}
                    )

        audit_log(
            "sql_executed",
            {
                "audit_id": audit_id,
                "sql": safe_sql,
                "execution_time_seconds": exec_res.execution_time_seconds,
                "row_count": len(exec_res.rows),
            },
        )

        # 7) Insight Generation
        insight = await insight_agent.run(
            question=question,
            sql=safe_sql,
            columns=exec_res.columns,
            rows=exec_res.rows
        )

        # 8) Visualization (Now aware of intent!)
        viz_decision = await viz_agent.decide(
            intent_json=intent.__dict__,
            question=question,
            columns=exec_res.columns,
            rows=exec_res.rows
        )

        try:
            chart_spec = viz_agent.to_plotly_spec(
                viz_decision, exec_res.columns, exec_res.rows
            )
        except Exception:
            chart_spec = None

        # 9) Recommendations
        recs = await rec_agent.run(
            question=question,
            answer=insight.answer,
            columns=exec_res.columns
        )

        return AskResponse(
            sql=safe_sql,
            sql_explanation=draft.explanation,
            answer=insight.answer,
            insights=insight.insights,
            chart_spec=chart_spec,
            recommendations=recs.recommendations,
            result=QueryResult(
                columns=exec_res.columns,
                rows=exec_res.rows,
                row_count=len(exec_res.rows),
                execution_time_seconds=exec_res.execution_time_seconds,
            ),
            audit_id=audit_id,
        )