"""FastAPI routes.

Endpoints:
- POST /connect-db
- POST /introspect
- POST /ask
- GET  /health

Auth:
- X-API-Key header (simple middleware-style dependency)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from text2sql_app.api.schemas import (
    AskRequest,
    AskResponse,
    ConnectDBRequest,
    ConnectDBResponse,
    IntrospectRequest,
    IntrospectResponse,
)
from text2sql_app.core.security import api_key_auth
from text2sql_app.services.connection_service import ConnectionService
from text2sql_app.services.orchestrator import Orchestrator

router = APIRouter(dependencies=[Depends(api_key_auth)])


@router.get("/health")
async def health() -> dict:
    return {"ok": True}


@router.post("/connect-db", response_model=ConnectDBResponse)
async def connect_db(req: ConnectDBRequest) -> ConnectDBResponse:
    svc = ConnectionService()
    await svc.connect_and_store(req.db_id, req.db_url, req.schema)
    return ConnectDBResponse(db_id=req.db_id, ok=True)


@router.post("/introspect", response_model=IntrospectResponse)
async def introspect(req: IntrospectRequest) -> IntrospectResponse:
    svc = ConnectionService()
    schema = await svc.introspect(req.db_id)
    return IntrospectResponse(db_id=req.db_id, tables=schema.table_count, columns=schema.column_count)


@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    orch = Orchestrator()
    return await orch.answer_question(req.db_id, req.question)