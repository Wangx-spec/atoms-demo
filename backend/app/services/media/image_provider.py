"""Image generation providers.

Each provider returns raw image bytes + a content type. The mock provider draws a
deterministic placeholder PNG so the pipeline is runnable without any external
service or API key.
"""
from __future__ import annotations

import asyncio
import hashlib
import struct
import zlib
from typing import Protocol

import httpx

from app.core.config import settings


class ImageProvider(Protocol):
    async def generate(self, prompt: str, params: dict) -> tuple[bytes, str]: ...


def _png_from_color(width: int, height: int, rgb: tuple[int, int, int]) -> bytes:
    """Build a minimal solid-color PNG without external libraries."""
    width = max(1, min(width, 1024))
    height = max(1, min(height, 1024))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    row = b"\x00" + bytes(rgb) * width
    raw = row * height
    idat = zlib.compress(raw, 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


class MockImageProvider:
    name = "mock"

    async def generate(self, prompt: str, params: dict) -> tuple[bytes, str]:
        digest = hashlib.sha256(prompt.encode("utf-8")).digest()
        rgb = (digest[0], digest[1], digest[2])
        width = int(params.get("width", 512))
        height = int(params.get("height", 512))
        return _png_from_color(width, height, rgb), "image/png"


class QwenImageProvider:
    """Alibaba DashScope text-to-image (Tongyi Wanxiang / 通义万相).

    DashScope text-to-image is asynchronous: we submit a job, poll the task id
    until it succeeds or fails, then download the resulting image bytes.
    """

    name = "qwen"

    SUBMIT_URL = (
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/"
        "text2image/image-synthesis"
    )
    TASK_URL = "https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"

    async def generate(self, prompt: str, params: dict) -> tuple[bytes, str]:
        if not settings.qwen_api_key:
            raise RuntimeError("QWEN_API_KEY required for qwen image provider")

        headers = {
            "Authorization": f"Bearer {settings.qwen_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.qwen_image_model,
            "input": {"prompt": prompt},
            "parameters": {
                "size": f"{params.get('width', 1024)}*{params.get('height', 1024)}",
                "n": 1,
            },
        }

        async with httpx.AsyncClient(timeout=settings.llm_request_timeout) as client:
            # 1. Submit the async job.
            submit = await client.post(
                self.SUBMIT_URL,
                headers={**headers, "X-DashScope-Async": "enable"},
                json=payload,
            )
            submit.raise_for_status()
            task_id = submit.json()["output"]["task_id"]

            # 2. Poll until the task reaches a terminal state.
            image_url = await self._poll(client, headers, task_id)

            # 3. Download the produced image bytes.
            img = await client.get(image_url)
            img.raise_for_status()
            return img.content, img.headers.get("content-type", "image/png")

    async def _poll(self, client: httpx.AsyncClient, headers: dict, task_id: str) -> str:
        deadline = settings.llm_request_timeout
        elapsed = 0.0
        interval = 2.0
        while elapsed < deadline:
            resp = await client.get(self.TASK_URL.format(task_id=task_id), headers=headers)
            resp.raise_for_status()
            output = resp.json().get("output", {})
            task_status = output.get("task_status")
            if task_status == "SUCCEEDED":
                results = output.get("results", [])
                if not results or "url" not in results[0]:
                    raise RuntimeError("Qwen image task succeeded without a result url")
                return results[0]["url"]
            if task_status in ("FAILED", "CANCELED", "UNKNOWN"):
                message = output.get("message", task_status)
                raise RuntimeError(f"Qwen image task {task_status}: {message}")
            await asyncio.sleep(interval)
            elapsed += interval
        raise RuntimeError("Qwen image task timed out")


class HttpImageProvider:
    """Generic adapter for ComfyUI / Stable Diffusion style HTTP endpoints."""

    def __init__(self, base_url: str, name: str) -> None:
        self._base_url = base_url.rstrip("/")
        self.name = name

    async def generate(self, prompt: str, params: dict) -> tuple[bytes, str]:
        if not self._base_url:
            raise RuntimeError(f"{self.name} base url not configured")
        async with httpx.AsyncClient(timeout=180) as client:
            resp = await client.post(
                f"{self._base_url}/generate", json={"prompt": prompt, **params}
            )
            resp.raise_for_status()
            return resp.content, resp.headers.get("content-type", "image/png")


def get_image_provider() -> ImageProvider:
    provider = settings.image_provider.lower()
    if provider == "qwen":
        return QwenImageProvider()
    if provider == "comfyui":
        return HttpImageProvider(settings.comfyui_base_url, "comfyui")
    if provider == "stablediffusion":
        return HttpImageProvider(settings.stablediffusion_base_url, "stablediffusion")
    return MockImageProvider()
