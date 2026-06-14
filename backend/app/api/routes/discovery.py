from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories.community import CommunityRepository
from app.schemas.gallery import GalleryItem
from app.services.vector_service import vector_service

router = APIRouter()


def _items(apps) -> list[GalleryItem]:
    return [GalleryItem.model_validate(app, from_attributes=True) for app in apps]


@router.get("/search", response_model=list[GalleryItem])
async def semantic_search(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
) -> list[GalleryItem]:
    repo = CommunityRepository(db)
    try:
        ids = await vector_service.search(q, limit=20)
        apps = await repo.get_by_ids([UUID(i) for i in ids])
        if apps:
            return _items(apps)
    except Exception:
        pass
    # Fallback to DB text search when the vector store is unavailable.
    return _items(await repo.text_search(q))


@router.get("/gallery/{app_id}/similar", response_model=list[GalleryItem])
async def similar_artworks(
    app_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[GalleryItem]:
    repo = CommunityRepository(db)
    try:
        ids = await vector_service.similar(app_id, limit=8)
        apps = await repo.get_by_ids([UUID(i) for i in ids if UUID(i) != app_id])
        if apps:
            return _items(apps)
    except Exception:
        pass
    return _items((await repo.list_public(sort="popular", limit=8)))


@router.get("/recommendations", response_model=list[GalleryItem])
async def recommendations(db: AsyncSession = Depends(get_db)) -> list[GalleryItem]:
    repo = CommunityRepository(db)
    return _items(await repo.list_public(sort="popular", limit=12))
