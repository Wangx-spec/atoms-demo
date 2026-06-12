from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.entities import TaskStatus


class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    status: TaskStatus
    progress: int
    result_url: str | None = None
    error_message: str | None = None
    created_at: datetime
