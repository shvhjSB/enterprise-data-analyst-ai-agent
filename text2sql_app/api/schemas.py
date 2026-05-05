"""Pydantic request/response schemas."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ConnectDBRequest(BaseModel):
    db_id: str = Field(..., description="Client-chosen identifier for this DB connection")
    db_url: str = Field(..., description="SQLAlchemy async URL, e.g. sqlite+aiosqlite:///./x.db")
    schema: Optional[str] = Field(default=None, description="Optional DB schema/catalog")


class ConnectDBResponse(BaseModel):
    db_id: str
    ok: bool


class IntrospectRequest(BaseModel):
    db_id: str


class IntrospectResponse(BaseModel):
    db_id: str
    tables: int
    columns: int


class AskRequest(BaseModel):
    db_id: str
    question: str


class QueryResult(BaseModel):
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    execution_time_seconds: float


class AskResponse(BaseModel):
    sql: str
    sql_explanation: str
    answer: str
    insights: List[str]
    chart_spec: Optional[Dict[str, Any]] = None
    recommendations: List[str]
    result: QueryResult
    audit_id: str