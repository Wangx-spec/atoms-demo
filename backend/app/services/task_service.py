"""Task orchestration: create a task row, then enqueue to Celery.

If the Celery broker is unavailable (common in keyless local dev), fall back to
running the task inline on the current event loop so the feature still works.
"""
from __future__ import annotations

import asyncio
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import UserORM
from app.repositories.media_artworks import MediaArtworkRepository
from app.repositories.tasks import TaskRepository
from app.schemas.tasks import CreateTaskRequest, TaskResponse, TaskType
from app.services import task_runner
from app.services.billing_service import BillingService
from app.services.storage_service import storage_service
from app.workers.celery_app import celery_app


class TaskService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.tasks = TaskRepository(db)
        self.media_artworks = MediaArtworkRepository(db)

    async def create_task(self, user: UserORM, payload: CreateTaskRequest) -> TaskResponse:
        # Charge credits for paid task types before enqueueing (raises 402 if short).
        billing = BillingService(self.db)
        cost = billing.cost_for(payload.type.value)
        await billing.charge(user, cost, reason=payload.type.value)

        task = await self.tasks.create(
            user_id=user.id,
            type=payload.type.value,
            status="pending",
            progress=0,
            params=payload.params,
        )
        self._dispatch(payload.type, task.id)
        return await self._to_response(task)

    async def list_tasks(self, user: UserORM) -> list[TaskResponse]:
        tasks = await self.tasks.list_by_user(user.id)
        return [await self._to_response(t) for t in tasks]

    async def get_task(self, user: UserORM, task_id: UUID) -> TaskResponse:
        task = await self._owned(user, task_id)
        return await self._to_response(task)

    async def _to_response(self, task) -> TaskResponse:
        """Serialize a task, signing a fresh presigned URL when a result exists.

        Results are stored as MinIO object keys in ``result_meta``; we sign a
        short-lived browser-reachable URL on every read so the link never
        outlives its expiry from the client's perspective.
        """
        response = TaskResponse.model_validate(task, from_attributes=True)
        object_key = (task.result_meta or {}).get("object_key")
        if object_key:
            try:
                response.result_url = storage_service.presigned_url(object_key)
            except Exception:
                response.result_url = None
        artwork = await self.media_artworks.get_by_task(task.id)
        if artwork:
            response.saved_artwork_id = artwork.id
        return response

    async def cancel_task(self, user: UserORM, task_id: UUID) -> TaskResponse:
        task = await self._owned(user, task_id)
        if task.status in ("succeeded", "failed"):
            return await self._to_response(task)
        updated = await self.tasks.update(task, {"status": "failed", "error_message": "cancelled"})
        return await self._to_response(updated)

    async def delete_task(self, user: UserORM, task_id: UUID) -> None:
        task = await self._owned(user, task_id)
        if task.status in ("pending", "running"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Running or pending tasks cannot be deleted; cancel them first",
            )
        await self.tasks.delete(task)

    async def _owned(self, user: UserORM, task_id: UUID):
        task = await self.tasks.get(task_id)
        if not task or task.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task

    def _dispatch(self, task_type: TaskType, task_id: UUID) -> None:
        enqueued = False
        if celery_app is not None:
            try:
                celery_app.send_task(task_type.value, args=[str(task_id)])
                enqueued = True
            except Exception:
                enqueued = False
        if not enqueued:
            # Inline fallback: run on the current event loop without blocking the response.
            runner = task_runner.RUNNERS[task_type.value]
            asyncio.create_task(runner(task_id))


task_service = None  # services are instantiated per-request with a db session
