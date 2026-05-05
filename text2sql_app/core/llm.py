"""Model-agnostic LLM client interface.

This module intentionally does NOT hardcode a specific vendor.
It provides:
- A minimal interface for structured JSON outputs.
- Provider selection via env settings.

Implementation note:
- For production you may integrate OpenAI Responses API, Azure OpenAI, Anthropic,
  or self-hosted models.
- This repository provides stubs that raise clear errors if not configured.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from text2sql_app.core.config import get_settings


class LLMError(RuntimeError):
    pass


@dataclass
class LLMResult:
    text: str
    json: Optional[Dict[str, Any]] = None


class LLMClient:
    async def complete_json(
        self,
        system: str,
        user: str,
        schema: Dict[str, Any],
        temperature: float = 0.0,
    ) -> LLMResult:
        raise NotImplementedError


class NotConfiguredLLM(LLMClient):
    async def complete_json(self, system: str, user: str, schema: Dict[str, Any], temperature: float = 0.0) -> LLMResult:
        raise LLMError(
            "LLM provider not configured. Set LLM_PROVIDER and provider API keys in env."
        )


def get_llm() -> LLMClient:
    settings = get_settings()

    # Keep provider implementations optional; error early if missing.
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            return NotConfiguredLLM()
        from text2sql_app.core.providers.openai_provider import OpenAIProvider

        return OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_model)

    if settings.llm_provider == "azure_openai":
        if not (settings.azure_openai_api_key and settings.azure_openai_endpoint and settings.azure_openai_deployment):
            return NotConfiguredLLM()
        from text2sql_app.core.providers.azure_openai_provider import AzureOpenAIProvider

        return AzureOpenAIProvider(
            api_key=settings.azure_openai_api_key,
            endpoint=settings.azure_openai_endpoint,
            deployment=settings.azure_openai_deployment,
        )

    if settings.llm_provider == "anthropic":
        if not settings.anthropic_api_key:
            return NotConfiguredLLM()
        from text2sql_app.core.providers.anthropic_provider import AnthropicProvider

        return AnthropicProvider(api_key=settings.anthropic_api_key, model=settings.anthropic_model)

    return NotConfiguredLLM()