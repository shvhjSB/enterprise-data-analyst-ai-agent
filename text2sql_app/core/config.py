"""Application configuration.

All sensitive configuration (API keys, master encryption key, LLM keys) must come
from environment variables or an external secret manager.

This module uses Pydantic Settings (v2).
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env", extra="ignore")

    # Security
    text2sql_app_master_key: str = Field(
        alias="TEXT2SQL_APP_MASTER_KEY",
        description="Master key used to derive a Fernet key to encrypt stored DB configs.",
    )
    text2sql_app_api_key: str = Field(
        alias="TEXT2SQL_APP_API_KEY",
        description="API key used for simple header-based auth.",
    )

    # Storage
    text2sql_app_data_dir: Path = Field(
        default=Path(".data"), alias="TEXT2SQL_APP_DATA_DIR", description="Local data dir"
    )

    # Execution limits
    text2sql_app_max_rows: int = Field(default=5000, alias="TEXT2SQL_APP_MAX_ROWS")
    text2sql_app_query_timeout_seconds: int = Field(
        default=30, alias="TEXT2SQL_APP_QUERY_TIMEOUT_SECONDS"
    )

    # LLM
    llm_provider: Literal["openai", "azure_openai", "anthropic"] = Field(
        default="openai", alias="LLM_PROVIDER"
    )
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")

    azure_openai_api_key: Optional[str] = Field(default=None, alias="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: Optional[str] = Field(default=None, alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment: Optional[str] = Field(default=None, alias="AZURE_OPENAI_DEPLOYMENT")

    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-latest", alias="ANTHROPIC_MODEL")

    # PII guardrails
    pii_allowlist: list[str] = Field(default_factory=list, alias="PII_ALLOWLIST")
    pii_denylist: list[str] = Field(default_factory=list, alias="PII_DENYLIST")


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.text2sql_app_data_dir.mkdir(parents=True, exist_ok=True)
    return _settings