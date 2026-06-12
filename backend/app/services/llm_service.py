import asyncio
from collections.abc import AsyncIterator
from typing import Protocol

from app.core.config import settings


class LLMProvider(Protocol):
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        ...


class MockLLMProvider:
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        chunks = [
            "正在分析需求...\n",
            f"用户需求：{prompt}\n",
            "正在规划界面结构...\n",
            "正在生成 HTML/CSS/JS 代码...\n",
            "生成完成，可以在右侧预览并继续编辑。\n",
        ]
        for chunk in chunks:
            await asyncio.sleep(0.25)
            yield chunk


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "mock":
        return MockLLMProvider()
    return MockLLMProvider()
