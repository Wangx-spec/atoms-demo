from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GeneratedCodePayload(BaseModel):
    html: str
    css: str = ""
    js: str = ""


class SaveGeneratedAppRequest(GeneratedCodePayload):
    prompt: str
    session_id: UUID | None = None
    status: str = "draft"


class GeneratedAppResponse(GeneratedCodePayload):
    id: UUID
    user_id: UUID
    session_id: UUID | None = None
    prompt: str
    preview_url: str | None = None
    status: str
    created_at: datetime
