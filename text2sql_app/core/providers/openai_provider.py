"""OpenAI provider implementation.

Uses HTTP calls via httpx to avoid hard-coupling to a specific SDK version.
You can replace this with official SDK usage.

NOTE: This is a minimal implementation for JSON-structured outputs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict

import httpx

from text2sql_app.core.llm import LLMClient, LLMError, LLMResult


@dataclass
class OpenAIProvider(LLMClient):
    api_key: str
    model: str

    async def complete_json(self, system: str, user: str, schema: Dict[str, Any], temperature: float = 0.0) -> LLMResult:
        # Using Chat Completions API with structured outputs (JSON mode).
        # For enterprise deployments, add retries, circuit breaker, and request IDs.
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_schema", "json_schema": {"name": "result", "schema": schema, "strict": True}},
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, headers=headers, json=payload)
            if r.status_code >= 400:
                raise LLMError(f"OpenAI error {r.status_code}: {r.text}")
            data = r.json()

        # Extract text output from Chat Completions API response
        # Structure: choices[0].message.content
        try:
            text_out = data["choices"][0]["message"]["content"]
            obj = json.loads(text_out)
        except (KeyError, json.JSONDecodeError) as e:
            raise LLMError(f"Failed to parse structured output: {e}")

        return LLMResult(text=text_out, json=obj)