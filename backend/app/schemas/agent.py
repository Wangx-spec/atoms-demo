from uuid import UUID

from pydantic import BaseModel

from app.models.entities import AgentMessage


class CreateSessionRequest(BaseModel):
    title: str | None = None


class AgentSessionResponse(BaseModel):
    id: UUID
    title: str
    messages: list[AgentMessage]


class SendMessageRequest(BaseModel):
    prompt: str


class SendMessageResponse(BaseModel):
    session_id: UUID
    stream_url: str
