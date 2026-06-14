from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_admin_user, get_db
from app.core.config import settings
from app.models.db import UserORM
from app.repositories.admin import AdminRepository
from app.schemas.admin import (
    AdminAppItem,
    AdminCreditAdjust,
    AdminTaskItem,
    AdminUser,
    AnnouncementItem,
    CreateAnnouncement,
    ModelConfig,
    ModerateRequest,
)

router = APIRouter()


@router.get("/stats")
async def admin_stats(
    _: UserORM = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await AdminRepository(db).stats()


@router.get("/users", response_model=list[AdminUser])
async def list_users(
    _: UserORM = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> list[AdminUser]:
    users = await AdminRepository(db).list_users()
    return [AdminUser.model_validate(u, from_attributes=True) for u in users]


@router.post("/users/{user_id}/credits", response_model=AdminUser)
async def adjust_credits(
    user_id: UUID,
    payload: AdminCreditAdjust,
    _: UserORM = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    user = await AdminRepository(db).adjust_credits(user_id, payload.delta)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return AdminUser.model_validate(user, from_attributes=True)


@router.post("/users/{user_id}/admin", response_model=AdminUser)
async def set_admin(
    user_id: UUID,
    is_admin: bool = True,
    _: UserORM = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    user = await AdminRepository(db).set_user_admin(user_id, is_admin)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return AdminUser.model_validate(user, from_attributes=True)


@router.get("/apps", response_model=list[AdminAppItem])
async def list_apps(
    status_filter: str | None = None,
    _: UserORM = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> list[AdminAppItem]:
    apps = await AdminRepository(db).list_apps(status=status_filter)
    return [AdminAppItem.model_validate(a, from_attributes=True) for a in apps]


@router.post("/apps/{app_id}/moderate", response_model=AdminAppItem)
async def moderate_app(
    app_id: UUID,
    payload: ModerateRequest,
    _: UserORM = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> AdminAppItem:
    app = await AdminRepository(db).moderate_app(app_id, payload.action)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="App not found")
    return AdminAppItem.model_validate(app, from_attributes=True)


@router.get("/tasks", response_model=list[AdminTaskItem])
async def list_tasks(
    _: UserORM = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> list[AdminTaskItem]:
    tasks = await AdminRepository(db).list_tasks()
    return [AdminTaskItem.model_validate(t, from_attributes=True) for t in tasks]


@router.get("/model-config", response_model=ModelConfig)
async def model_config(_: UserORM = Depends(get_admin_user)) -> ModelConfig:
    return ModelConfig(
        llm_provider=settings.llm_provider,
        deepseek_model=settings.deepseek_model,
        qwen_model=settings.qwen_model,
        image_provider=settings.image_provider,
        music_provider=settings.music_provider,
        embedding_provider=settings.embedding_provider,
    )


@router.get("/announcements", response_model=list[AnnouncementItem])
async def list_announcements(
    _: UserORM = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> list[AnnouncementItem]:
    items = await AdminRepository(db).list_announcements()
    return [AnnouncementItem.model_validate(i, from_attributes=True) for i in items]


@router.post("/announcements", response_model=AnnouncementItem)
async def create_announcement(
    payload: CreateAnnouncement,
    _: UserORM = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> AnnouncementItem:
    item = await AdminRepository(db).create_announcement(payload.title, payload.body)
    return AnnouncementItem.model_validate(item, from_attributes=True)


@router.delete("/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement(
    announcement_id: UUID,
    _: UserORM = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    ok = await AdminRepository(db).delete_announcement(announcement_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")
