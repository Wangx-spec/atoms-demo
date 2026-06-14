from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SaveTaskAsArtworkRequest(BaseModel):
    title: str | None = None
    visibility: str = "private"


class MediaArtworkResponse(BaseModel):
    id: UUID
    user_id: UUID
    source_task_id: UUID | None = None
    type: str
    prompt: str
    title: str | None = None
    params: dict = {}
    content_type: str
    media_url: str | None = None
    visibility: str = "private"
    created_at: datetime
    updated_at: datetime
