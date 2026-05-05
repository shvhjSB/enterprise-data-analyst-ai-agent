"""Connection storage + schema cache service."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from text2sql_app.core.config import get_settings
from text2sql_app.core.db import reflect_schema, test_connection
from text2sql_app.core.security import EncryptedStore
from text2sql_app.core.schema_models import SchemaSnapshot, build_schema_snapshot


@dataclass
class StoredConn:
    db_url: str
    schema: Optional[str] = None


class ConnectionService:
    def __init__(self) -> None:
        settings = get_settings()
        self._store = EncryptedStore(settings.text2sql_app_data_dir / "connections.enc.json")
        self._schema_store = EncryptedStore(settings.text2sql_app_data_dir / "schemas.enc.json")

    async def connect_and_store(self, db_id: str, db_url: str, schema: str | None) -> None:
        await test_connection(db_url)
        all_conns = self._store.load_all()
        all_conns[db_id] = {"db_url": db_url, "schema": schema}
        self._store.save_all(all_conns)

    def get_db_url(self, db_id: str) -> str:
        all_conns = self._store.load_all()
        if db_id not in all_conns:
            raise KeyError(f"Unknown db_id: {db_id}")
        return all_conns[db_id]["db_url"]

    def get_schema_name(self, db_id: str) -> str | None:
        all_conns = self._store.load_all()
        if db_id not in all_conns:
            raise KeyError(f"Unknown db_id: {db_id}")
        return all_conns[db_id].get("schema")

    async def introspect(self, db_id: str) -> SchemaSnapshot:
        db_url = self.get_db_url(db_id)
        schema_name = self.get_schema_name(db_id)
        md = await reflect_schema(db_url, schema=schema_name)
        snapshot = build_schema_snapshot(md)

        all_schemas = self._schema_store.load_all()
        all_schemas[db_id] = snapshot.model_dump()
        self._schema_store.save_all(all_schemas)
        return snapshot

    def load_cached_schema(self, db_id: str) -> SchemaSnapshot:
        all_schemas = self._schema_store.load_all()
        if db_id not in all_schemas:
            raise KeyError(f"Schema not cached for db_id: {db_id}. Call /introspect")
        return SchemaSnapshot.model_validate(all_schemas[db_id])