"""Celery task entrypoints.

Each task wraps the shared async runner with ``asyncio.run`` since Celery workers
are synchronous processes.
"""
from __future__ import annotations

import asyncio
from uuid import UUID

from app.services import task_runner
from app.workers.celery_app import celery_app


def _run(coro_fn, task_id: str) -> None:
    """Run an async runner in a fresh event loop and dispose the engine after.

    Disposing the async engine prevents asyncpg connections from being reused
    across event loops (each ``asyncio.run`` creates and tears down a loop),
    which otherwise raises ``got Future attached to a different loop``.
    """
    from app.db.session import engine

    async def runner():
        try:
            await coro_fn(UUID(task_id))
        finally:
            await engine.dispose()

    asyncio.run(runner())


def _run_coro(coro_fn, arg) -> None:
    from app.db.session import engine

    async def runner():
        try:
            await coro_fn(arg)
        finally:
            await engine.dispose()

    asyncio.run(runner())


if celery_app:

    @celery_app.task(name="code_generation")
    def code_generation(task_id: str) -> None:
        _run(task_runner.run_code_generation, task_id)

    @celery_app.task(name="image_generation")
    def image_generation(task_id: str) -> None:
        _run(task_runner.run_image_generation, task_id)

    @celery_app.task(name="music_generation")
    def music_generation(task_id: str) -> None:
        _run(task_runner.run_music_generation, task_id)

    @celery_app.task(name="preview_snapshot")
    def preview_snapshot(task_id: str) -> None:
        _run(task_runner.run_preview_snapshot, task_id)

    @celery_app.task(name="embed_artwork")
    def embed_artwork(app_id: str) -> None:
        from app.services.vector_service import run_embed_artwork

        _run_coro(run_embed_artwork, UUID(app_id))
