from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel

from app.models.entities import TaskStatus


class TaskType(StrEnum):
    code_generation = "code_generation"
    image_generation = "image_generation"
    music_generation = "music_generation"
    preview_snapshot = "preview_snapshot"


class CreateTaskRequest(BaseModel):
    type: TaskType
    params: dict = {}


class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    status: TaskStatus
    progress: int
    result_url: str | None = None
    saved_artwork_id: UUID | None = None
    error_message: str | None = None
    params: dict = {}
    result_meta: dict = {}
    created_at: datetime
