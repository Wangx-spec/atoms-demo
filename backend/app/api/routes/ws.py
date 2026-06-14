import asyncio
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.db.session import async_session
from app.repositories.tasks import TaskRepository

router = APIRouter()


@router.websocket("/events")
async def websocket_events(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({"type": "connected", "message": "Atoms realtime channel ready"})
    await websocket.close()


@router.websocket("/tasks/{task_id}")
async def websocket_task_progress(websocket: WebSocket, task_id: str) -> None:
    """Push task progress over WebSocket until the task reaches a terminal state."""
    await websocket.accept()
    try:
        for _ in range(600):
            async with async_session() as db:
                task = await TaskRepository(db).get(UUID(task_id))
            if task is None:
                await websocket.send_json({"type": "error", "detail": "task not found"})
                break
            await websocket.send_json(
                {
                    "type": "progress",
                    "id": str(task.id),
                    "status": task.status,
                    "progress": task.progress,
                    "result_url": task.result_url,
                }
            )
            if task.status in ("succeeded", "failed"):
                break
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
    finally:
        await websocket.close()
