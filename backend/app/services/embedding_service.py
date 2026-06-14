"""Embedding providers.

MockEmbedding produces deterministic hash-based pseudo-vectors so semantic search
runs without any external model. QwenEmbedding calls the DashScope OpenAI-compatible
embeddings endpoint.
"""
from __future__ import annotations

import hashlib
import math
from typing import Protocol

import httpx

from app.core.config import settings


class EmbeddingProvider(Protocol):
    async def embed(self, text: str) -> list[float]: ...


class MockEmbedding:
    name = "mock"

    def __init__(self, dim: int | None = None) -> None:
        self.dim = dim or settings.embedding_dim

    async def embed(self, text: str) -> list[float]:
        # Deterministic pseudo-vector from repeated hashing, L2-normalized.
        vector: list[float] = []
        seed = text.encode("utf-8")
        while len(vector) < self.dim:
            seed = hashlib.sha256(seed).digest()
            vector.extend(b / 255.0 - 0.5 for b in seed)
        vector = vector[: self.dim]
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


class QwenEmbedding:
    name = "qwen"

    def __init__(self) -> None:
        self.dim = settings.embedding_dim

    async def embed(self, text: str) -> list[float]:
        if not settings.qwen_api_key:
            raise RuntimeError("QWEN_API_KEY required for qwen embedding provider")
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{settings.qwen_base_url.rstrip('/')}/embeddings",
                headers={"Authorization": f"Bearer {settings.qwen_api_key}"},
                json={"model": "text-embedding-v2", "input": text},
            )
            resp.raise_for_status()
            return resp.json()["data"][0]["embedding"]


def get_embedding_provider() -> EmbeddingProvider:
    if settings.embedding_provider.lower() == "qwen":
        return QwenEmbedding()
    return MockEmbedding()
