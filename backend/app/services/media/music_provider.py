"""Music generation providers.

The mock provider emits a short silent WAV so the pipeline runs without any
external service. Real adapters (Suno / MusicGen / Riffusion) call HTTP APIs.
"""
from __future__ import annotations

import asyncio
import struct
from typing import Protocol

import httpx

from app.core.config import settings


class MusicProvider(Protocol):
    async def generate(self, prompt: str, params: dict) -> tuple[bytes, str]: ...


def _silent_wav(seconds: int, sample_rate: int = 8000) -> tuple[bytes, str]:
    seconds = max(1, min(seconds, 60))
    num_samples = seconds * sample_rate
    data = b"\x00\x00" * num_samples
    byte_rate = sample_rate * 2
    header = b"RIFF"
    header += struct.pack("<I", 36 + len(data))
    header += b"WAVE"
    header += b"fmt "
    header += struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, byte_rate, 2, 16)
    header += b"data"
    header += struct.pack("<I", len(data))
    return header + data, "audio/wav"


class MockMusicProvider:
    name = "mock"

    async def generate(self, prompt: str, params: dict) -> tuple[bytes, str]:
        return _silent_wav(int(params.get("duration", 8)))


class SunoMusicProvider:
    """Suno-style async music API: submit a job, poll, then download audio.

    Field names vary across Suno-compatible gateways; adjust ``_extract_*`` and
    payload keys to match the concrete service in use (noted in the readme).
    """

    name = "suno"

    SUBMIT_URL = "https://api.suno.ai/v1/generate"
    STATUS_URL = "https://api.suno.ai/v1/tasks/{task_id}"

    async def generate(self, prompt: str, params: dict) -> tuple[bytes, str]:
        if not settings.suno_api_key:
            raise RuntimeError("SUNO_API_KEY required for suno music provider")
        headers = {"Authorization": f"Bearer {settings.suno_api_key}"}
        async with httpx.AsyncClient(timeout=settings.llm_request_timeout) as client:
            submit = await client.post(
                self.SUBMIT_URL, headers=headers, json={"prompt": prompt, **params}
            )
            submit.raise_for_status()
            data = submit.json()

            # Some gateways return the audio URL synchronously; otherwise poll.
            audio_url = self._extract_audio_url(data)
            if not audio_url:
                task_id = data.get("task_id") or data.get("id")
                if not task_id:
                    raise RuntimeError("Suno response missing task id and audio url")
                audio_url = await self._poll(client, headers, task_id)

            audio = await client.get(audio_url)
            audio.raise_for_status()
            return audio.content, audio.headers.get("content-type", "audio/mpeg")

    async def _poll(self, client: httpx.AsyncClient, headers: dict, task_id: str) -> str:
        deadline = settings.llm_request_timeout
        elapsed = 0.0
        interval = 3.0
        while elapsed < deadline:
            resp = await client.get(
                self.STATUS_URL.format(task_id=task_id), headers=headers
            )
            resp.raise_for_status()
            data = resp.json()
            status = (data.get("status") or "").lower()
            if status in ("failed", "error"):
                raise RuntimeError(f"Suno task failed: {data.get('message', status)}")
            audio_url = self._extract_audio_url(data)
            if audio_url:
                return audio_url
            await asyncio.sleep(interval)
            elapsed += interval
        raise RuntimeError("Suno task timed out")

    @staticmethod
    def _extract_audio_url(data: dict) -> str | None:
        if data.get("audio_url"):
            return data["audio_url"]
        output = data.get("output") or data.get("data") or {}
        if isinstance(output, dict) and output.get("audio_url"):
            return output["audio_url"]
        if isinstance(output, list) and output and isinstance(output[0], dict):
            return output[0].get("audio_url")
        return None


class MusicGenProvider:
    """Generic HTTP adapter for a self-hosted MusicGen-style endpoint.

    Expects ``POST {base_url}/generate`` to return audio bytes directly.
    """

    name = "musicgen"

    async def generate(self, prompt: str, params: dict) -> tuple[bytes, str]:
        base_url = settings.musicgen_base_url.rstrip("/")
        if not base_url:
            raise RuntimeError("MUSICGEN_BASE_URL required for musicgen provider")
        async with httpx.AsyncClient(timeout=settings.llm_request_timeout) as client:
            resp = await client.post(
                f"{base_url}/generate", json={"prompt": prompt, **params}
            )
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "audio/wav")
            if content_type.startswith("application/json"):
                # Endpoint returned a URL instead of raw bytes.
                data = resp.json()
                audio_url = data.get("audio_url") or data.get("url")
                if not audio_url:
                    raise RuntimeError("MusicGen response missing audio url")
                audio = await client.get(audio_url)
                audio.raise_for_status()
                return audio.content, audio.headers.get("content-type", "audio/wav")
            return resp.content, content_type


def get_music_provider() -> MusicProvider:
    provider = settings.music_provider.lower()
    if provider == "suno":
        return SunoMusicProvider()
    if provider == "musicgen":
        return MusicGenProvider()
    return MockMusicProvider()
