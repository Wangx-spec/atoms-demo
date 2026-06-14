from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GalleryItem(BaseModel):
    id: UUID
    user_id: UUID
    title: str | None = None
    prompt: str
    tags: str | None = None
    preview_url: str | None = None
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    published_at: datetime | None = None


class CommentResponse(BaseModel):
    id: UUID
    user_id: UUID
    app_id: UUID
    content: str
    created_at: datetime


class GalleryDetail(GalleryItem):
    html: str
    css: str = ""
    js: str = ""
    runtime: str = "static-html"
    liked: bool = False
    comments: list[CommentResponse] = []


class CreateCommentRequest(BaseModel):
    content: str


class ProfileResponse(BaseModel):
    user_id: UUID
    display_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    public_app_count: int = 0
    apps: list[GalleryItem] = []


class UpdateProfileRequest(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
