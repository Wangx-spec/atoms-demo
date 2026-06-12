from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class TaskStatus(StrEnum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: str
    password_hash: str
    credits: int = 100
    avatar_url: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class AgentMessage(BaseModel):
    role: str
    content: str
    created_at: datetime = Field(default_factory=utc_now)


class AgentSession(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    title: str
    messages: list[AgentMessage] = Field(default_factory=list)
    context: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class GeneratedApp(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    session_id: UUID | None = None
    prompt: str
    html: str
    css: str = ""
    js: str = ""
    preview_url: str | None = None
    status: str = "draft"
    created_at: datetime = Field(default_factory=utc_now)


class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    type: str
    status: TaskStatus = TaskStatus.pending
    progress: int = 0
    result_url: str | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
