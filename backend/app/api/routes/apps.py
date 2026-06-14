from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.db import UserORM
from app.schemas.apps import (
    GeneratedAppResponse,
    SaveGeneratedAppRequest,
    UpdateGeneratedAppRequest,
)
from app.services.app_service import AppService

router = APIRouter()


@router.post("", response_model=GeneratedAppResponse)
async def save_app(
    payload: SaveGeneratedAppRequest,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GeneratedAppResponse:
    return await AppService(db).save_app(current_user, payload)


@router.get("", response_model=list[GeneratedAppResponse])
async def list_apps(
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[GeneratedAppResponse]:
    return await AppService(db).list_apps(current_user)


@router.get("/{app_id}", response_model=GeneratedAppResponse)
async def get_app(
    app_id: UUID,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GeneratedAppResponse:
    return await AppService(db).get_app(current_user, app_id)


@router.patch("/{app_id}", response_model=GeneratedAppResponse)
async def update_app(
    app_id: UUID,
    payload: UpdateGeneratedAppRequest,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GeneratedAppResponse:
    return await AppService(db).update_app(current_user, app_id, payload)


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app(
    app_id: UUID,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await AppService(db).delete_app(current_user, app_id)
