from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.db import UserORM
from app.schemas.media_artworks import MediaArtworkResponse, SaveTaskAsArtworkRequest
from app.services.media_artwork_service import MediaArtworkService

router = APIRouter()


@router.post("/from-task/{task_id}", response_model=MediaArtworkResponse)
async def save_from_task(
    task_id: UUID,
    payload: SaveTaskAsArtworkRequest,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MediaArtworkResponse:
    return await MediaArtworkService(db).save_from_task(current_user, task_id, payload)


@router.get("", response_model=list[MediaArtworkResponse])
async def list_artworks(
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MediaArtworkResponse]:
    return await MediaArtworkService(db).list_artworks(current_user)


@router.delete("/{artwork_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artwork(
    artwork_id: UUID,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await MediaArtworkService(db).delete_artwork(current_user, artwork_id)
