import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.db.session import async_session
from app.models.db import UserORM
from app.repositories.tasks import TaskRepository
from app.schemas.tasks import CreateTaskRequest, TaskResponse
from app.services.storage_service import storage_service
from app.services.task_service import TaskService

router = APIRouter()


@router.post("", response_model=TaskResponse)
async def create_task(
    payload: CreateTaskRequest,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    return await TaskService(db).create_task(current_user, payload)


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TaskResponse]:
    return await TaskService(db).list_tasks(current_user)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    return await TaskService(db).get_task(current_user, task_id)


@router.post("/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(
    task_id: UUID,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    return await TaskService(db).cancel_task(current_user, task_id)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await TaskService(db).delete_task(current_user, task_id)


@router.get("/{task_id}/stream")
async def stream_task(
    task_id: UUID,
    current_user: UserORM = Depends(get_current_user),
) -> StreamingResponse:
    async def event_stream():
        for _ in range(600):  # ~10 min cap at 1s interval
            async with async_session() as db:
                task = await TaskRepository(db).get(task_id)
            if not task or task.user_id != current_user.id:
                yield 'event: error\ndata: {"detail":"not found"}\n\n'
                return
            result_url = None
            object_key = (task.result_meta or {}).get("object_key")
            if object_key:
                try:
                    result_url = storage_service.presigned_url(object_key)
                except Exception:
                    result_url = None
            payload = (
                f'{{"id":"{task.id}","status":"{task.status}",'
                f'"progress":{task.progress},"result_url":{_json(result_url)}}}'
            )
            yield f"event: progress\ndata: {payload}\n\n"
            if task.status in ("succeeded", "failed"):
                yield "event: done\ndata: ok\n\n"
                return
            await asyncio.sleep(1)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _json(value: str | None) -> str:
    return f'"{value}"' if value else "null"
