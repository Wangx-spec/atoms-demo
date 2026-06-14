"""LLM provider abstraction.

Unified async interface used by the agent graph and codegen service:
    - ``stream(prompt)``       -> token stream (AsyncIterator[str])
    - ``complete(prompt)``     -> full text completion
    - ``generate_json(prompt, schema)`` -> parsed JSON object

Providers:
    - DeepSeekProvider / QwenProvider : OpenAI-compatible chat completions via httpx.
    - MockLLMProvider                 : keyless local fallback.
"""
from __future__ import annotations

import asyncio
import json
import re
from collections.abc import AsyncIterator
from typing import Any, Protocol, runtime_checkable

import httpx

from app.core.config import settings


class LLMError(RuntimeError):
    pass


@runtime_checkable
class LLMProvider(Protocol):
    async def stream(self, prompt: str, system: str | None = None) -> AsyncIterator[str]: ...

    async def complete(self, prompt: str, system: str | None = None) -> str: ...

    async def generate_json(
        self, prompt: str, schema_hint: str | None = None, system: str | None = None
    ) -> dict[str, Any]: ...


def _extract_json(text: str) -> dict[str, Any]:
    """Best-effort JSON extraction from a model response."""
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidate = fenced.group(1) if fenced else None
    if candidate is None:
        brace = re.search(r"\{.*\}", text, re.DOTALL)
        candidate = brace.group(0) if brace else text
    return json.loads(candidate)


class _OpenAICompatibleProvider:
    """Shared implementation for OpenAI-compatible chat APIs (DeepSeek, Qwen)."""

    name = "openai-compatible"

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model

    def _require_key(self) -> None:
        if not self._api_key:
            raise LLMError(
                f"{self.name} provider is selected but no API key is configured. "
                "Set the corresponding *_API_KEY, or use LLM_PROVIDER=mock for local dev."
            )

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

    def _messages(self, prompt: str, system: str | None) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return messages

    async def stream(self, prompt: str, system: str | None = None) -> AsyncIterator[str]:
        self._require_key()
        payload = {
            "model": self._model,
            "messages": self._messages(prompt, system),
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=settings.llm_request_timeout) as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            ) as response:
                if response.status_code >= 400:
                    body = await response.aread()
                    raise LLMError(f"{self.name} stream error {response.status_code}: {body!r}")
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[len("data:"):].strip()
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"].get("content")
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
                    if delta:
                        yield delta

    async def complete(self, prompt: str, system: str | None = None) -> str:
        self._require_key()
        payload = {"model": self._model, "messages": self._messages(prompt, system)}
        async with httpx.AsyncClient(timeout=settings.llm_request_timeout) as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            if response.status_code >= 400:
                raise LLMError(f"{self.name} error {response.status_code}: {response.text}")
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def generate_json(
        self, prompt: str, schema_hint: str | None = None, system: str | None = None
    ) -> dict[str, Any]:
        instruction = (
            "You must respond with a single valid JSON object and nothing else."
            + (f" The JSON schema is: {schema_hint}" if schema_hint else "")
        )
        full_system = f"{system}\n{instruction}" if system else instruction
        text = await self.complete(prompt, system=full_system)
        try:
            return _extract_json(text)
        except (json.JSONDecodeError, ValueError):
            # one automatic repair attempt
            repair = await self.complete(
                f"Convert the following into a single valid JSON object only:\n{text}",
                system=instruction,
            )
            return _extract_json(repair)


class DeepSeekProvider(_OpenAICompatibleProvider):
    name = "deepseek"

    def __init__(self) -> None:
        super().__init__(settings.deepseek_api_key, settings.deepseek_base_url, settings.deepseek_model)


class QwenProvider(_OpenAICompatibleProvider):
    name = "qwen"

    def __init__(self) -> None:
        super().__init__(settings.qwen_api_key, settings.qwen_base_url, settings.qwen_model)


class MockLLMProvider:
    name = "mock"

    async def stream(self, prompt: str, system: str | None = None) -> AsyncIterator[str]:
        chunks = [
            "正在分析需求...\n",
            f"用户需求：{prompt}\n",
            "正在规划界面结构...\n",
            "正在生成 HTML/CSS/JS 代码...\n",
            "生成完成，可以在右侧预览并继续编辑。\n",
        ]
        for chunk in chunks:
            await asyncio.sleep(0.2)
            yield chunk

    async def complete(self, prompt: str, system: str | None = None) -> str:
        return f"Mock completion for: {prompt[:80]}"

    async def generate_json(
        self, prompt: str, schema_hint: str | None = None, system: str | None = None
    ) -> dict[str, Any]:
        return {"mock": True, "prompt": prompt[:120]}


def get_llm_provider() -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider == "deepseek":
        return DeepSeekProvider()
    if provider == "qwen":
        return QwenProvider()
    return MockLLMProvider()
