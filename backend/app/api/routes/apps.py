from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.entities import User
from app.schemas.apps import GeneratedAppResponse, SaveGeneratedAppRequest
from app.services.app_service import app_service

router = APIRouter()


@router.post("", response_model=GeneratedAppResponse)
async def save_app(
    payload: SaveGeneratedAppRequest,
    current_user: User = Depends(get_current_user),
) -> GeneratedAppResponse:
    return app_service.save_app(current_user, payload)


@router.get("", response_model=list[GeneratedAppResponse])
async def list_apps(current_user: User = Depends(get_current_user)) -> list[GeneratedAppResponse]:
    return app_service.list_apps(current_user)


@router.get("/{app_id}", response_model=GeneratedAppResponse)
async def get_app(
    app_id: UUID,
    current_user: User = Depends(get_current_user),
) -> GeneratedAppResponse:
    return app_service.get_app(current_user, app_id)
