from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AdminUser(BaseModel):
    id: UUID
    email: str
    credits: int
    is_admin: bool
    created_at: datetime


class AdminCreditAdjust(BaseModel):
    delta: int


class AdminAppItem(BaseModel):
    id: UUID
    user_id: UUID
    prompt: str
    status: str
    visibility: str
    created_at: datetime


class AdminTaskItem(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    status: str
    progress: int
    created_at: datetime


class ModerateRequest(BaseModel):
    action: str  # approve | reject


class AnnouncementItem(BaseModel):
    id: UUID
    title: str
    body: str
    published: bool
    created_at: datetime


class CreateAnnouncement(BaseModel):
    title: str
    body: str = ""


class ModelConfig(BaseModel):
    llm_provider: str
    deepseek_model: str
    qwen_model: str
    image_provider: str
    music_provider: str
    embedding_provider: str
