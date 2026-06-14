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
    runtime: str = "static-html"


class UpdateGeneratedAppRequest(BaseModel):
    prompt: str | None = None
    html: str | None = None
    css: str | None = None
    js: str | None = None
    status: str | None = None
    runtime: str | None = None
    visibility: str | None = None


class GeneratedAppResponse(GeneratedCodePayload):
    id: UUID
    user_id: UUID
    session_id: UUID | None = None
    prompt: str
    preview_url: str | None = None
    status: str
    runtime: str = "static-html"
    visibility: str = "private"
    title: str | None = None
    tags: str | None = None
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    created_at: datetime
    updated_at: datetime
