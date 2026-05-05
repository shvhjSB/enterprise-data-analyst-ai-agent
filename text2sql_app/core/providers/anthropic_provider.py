"""Anthropic provider stub."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from text2sql_app.core.llm import LLMClient, LLMError, LLMResult


@dataclass
class AnthropicProvider(LLMClient):
    api_key: str
    model: str

    async def complete_json(self, system: str, user: str, schema: Dict[str, Any], temperature: float = 0.0) -> LLMResult:
        raise LLMError("Anthropic provider not implemented in this scaffold. Plug in your SDK/REST here.")