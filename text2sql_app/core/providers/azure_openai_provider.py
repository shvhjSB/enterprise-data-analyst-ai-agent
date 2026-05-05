"""Azure OpenAI provider stub.

Implementations differ by API version and resource configuration.
This stub shows where to integrate your Azure OpenAI calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from text2sql_app.core.llm import LLMClient, LLMError, LLMResult


@dataclass
class AzureOpenAIProvider(LLMClient):
    api_key: str
    endpoint: str
    deployment: str

    async def complete_json(self, system: str, user: str, schema: Dict[str, Any], temperature: float = 0.0) -> LLMResult:
        raise LLMError("Azure OpenAI provider not implemented in this scaffold. Plug in your SDK/REST here.")