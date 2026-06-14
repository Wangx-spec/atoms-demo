from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.entities import AgentMessage


class CreateSessionRequest(BaseModel):
    title: str | None = None


class UpdateSessionRequest(BaseModel):
    title: str


class AgentSessionResponse(BaseModel):
    id: UUID
    title: str
    messages: list[AgentMessage]


class AgentSessionSummary(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class SendMessageRequest(BaseModel):
    prompt: str


class SendMessageResponse(BaseModel):
    session_id: UUID
    stream_url: str
