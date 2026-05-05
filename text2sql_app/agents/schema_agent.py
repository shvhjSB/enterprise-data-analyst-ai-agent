"""Schema Intelligence Agent.

Responsibilities:
- Load cached schema snapshot (or instruct to introspect)
- Provide semantic schema representation to downstream agents

In this scaffold, schema introspection is done by ConnectionService; this agent
wraps it for orchestration consistency.
"""

from __future__ import annotations

from dataclasses import dataclass

from text2sql_app.core.schema_models import SchemaSnapshot
from text2sql_app.services.connection_service import ConnectionService


@dataclass
class SchemaContext:
    snapshot: SchemaSnapshot


class SchemaIntelligenceAgent:
    async def run(self, db_id: str) -> SchemaContext:
        svc = ConnectionService()
        snapshot = svc.load_cached_schema(db_id)
        return SchemaContext(snapshot=snapshot)