"""Async task implementations shared by Celery workers and the inline fallback.

Each runner opens its own DB session, updates the ``tasks`` row as it progresses,
generates the artifact, uploads results to MinIO and records the storage URL.
"""
from __future__ import annotations

import asyncio
from uuid import UUID

from app.db.session import async_session
from app.repositories.tasks import TaskRepository
from app.services.codegen_service import codegen_service
from app.services.media.image_provider import get_image_provider
from app.services.media.music_provider import get_music_provider
from app.services.storage_service import storage_service


async def _set(repo: TaskRepository, task, **data):
    await repo.update(task, data)


async def _run(task_id: UUID, worker) -> None:
    async with async_session() as db:
        repo = TaskRepository(db)
        task = None
        try:
            task = await repo.get(task_id)
            if task is None:
                return
            await _set(repo, task, status="running", progress=10)
            await worker(repo, task)
        except Exception as exc:  # record failure on the task row
            # ``task`` may be None if ``repo.get`` failed; guard so the failure
            # is still persisted whenever the row was fetched.
            if task is not None:
                try:
                    await _set(
                        repo,
                        task,
                        status="failed",
                        error_message=str(exc),
                        progress=100,
                    )
                except Exception:
                    # Best-effort: avoid masking the original error if the
                    # failure write itself cannot complete.
                    pass
            raise


async def run_code_generation(task_id: UUID) -> None:
    async def worker(repo, task):
        prompt = task.params.get("prompt", "")
        await _set(repo, task, progress=40)
        code = await codegen_service.generate_app(prompt)
        await _set(
            repo,
            task,
            status="succeeded",
            progress=100,
            result_meta={"html": code.html, "css": code.css, "js": code.js},
        )

    await _run(task_id, worker)


async def run_image_generation(task_id: UUID) -> None:
    async def worker(repo, task):
        prompt = task.params.get("prompt", "")
        await _set(repo, task, progress=40)
        data, content_type = await get_image_provider().generate(prompt, task.params)
        ext = "png" if "png" in content_type else "jpg"
        object_key = await asyncio.to_thread(
            storage_service.upload_bytes, data, content_type, ext
        )
        await _set(
            repo,
            task,
            status="succeeded",
            progress=100,
            result_meta={"object_key": object_key, "content_type": content_type},
        )

    await _run(task_id, worker)


async def run_music_generation(task_id: UUID) -> None:
    async def worker(repo, task):
        prompt = task.params.get("prompt", "")
        await _set(repo, task, progress=40)
        data, content_type = await get_music_provider().generate(prompt, task.params)
        ext = "wav" if "wav" in content_type else "mp3"
        object_key = await asyncio.to_thread(
            storage_service.upload_bytes, data, content_type, ext
        )
        await _set(
            repo,
            task,
            status="succeeded",
            progress=100,
            result_meta={"object_key": object_key, "content_type": content_type},
        )

    await _run(task_id, worker)


async def run_preview_snapshot(task_id: UUID) -> None:
    async def worker(repo, task):
        await _set(
            repo,
            task,
            status="succeeded",
            progress=100,
            result_meta={"note": "preview snapshot placeholder"},
        )

    await _run(task_id, worker)


RUNNERS = {
    "code_generation": run_code_generation,
    "image_generation": run_image_generation,
    "music_generation": run_music_generation,
    "preview_snapshot": run_preview_snapshot,
}
