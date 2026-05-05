import os
import sqlite3
import pytest

from text2sql_app.services.connection_service import ConnectionService


@pytest.mark.asyncio
async def test_connection_and_introspection(tmp_path, monkeypatch):
    # Create a small SQLite DB
    db_file = tmp_path / "t.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, amount REAL, created_at TEXT)")
    cur.execute("INSERT INTO orders(amount, created_at) VALUES (10.0, '2025-01-01')")
    conn.commit()
    conn.close()

    monkeypatch.setenv("TEXT2SQL_APP_MASTER_KEY", "unit-test-master-key")
    monkeypatch.setenv("TEXT2SQL_APP_API_KEY", "unit-test-api-key")
    monkeypatch.setenv("TEXT2SQL_APP_DATA_DIR", str(tmp_path / ".data"))

    svc = ConnectionService()
    db_url = f"sqlite+aiosqlite:///{db_file}"
    await svc.connect_and_store("db", db_url, None)
    snap = await svc.introspect("db")
    assert snap.table_count == 1
    assert snap.column_count >= 3