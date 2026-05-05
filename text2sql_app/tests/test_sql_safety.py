import pytest

from text2sql_app.core.sql_safety import is_destructive, enforce_limit, validate_and_rewrite


def test_destructive_blocked():
    assert is_destructive("DROP TABLE users;") is True
    assert validate_and_rewrite("DELETE FROM t", max_rows=10).ok is False


def test_limit_enforced():
    sql = "SELECT 1"
    out = enforce_limit(sql, 100)
    assert "LIMIT 100" in out.upper()


def test_limit_not_duplicated():
    sql = "SELECT * FROM x LIMIT 10"
    out = enforce_limit(sql, 100)
    assert out == sql


def test_pii_block():
    res = validate_and_rewrite("SELECT email FROM users", max_rows=10, blocked_columns={"email"})
    assert res.ok is False