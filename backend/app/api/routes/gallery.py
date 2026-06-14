from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, get_optional_user
from app.models.db import GeneratedAppORM, UserORM
from app.repositories.community import CommunityRepository
from app.repositories.users import UserRepository
from app.schemas.gallery import (
    CommentResponse,
    CreateCommentRequest,
    GalleryDetail,
    GalleryItem,
    ProfileResponse,
    UpdateProfileRequest,
)

router = APIRouter()


def _to_item(app: GeneratedAppORM) -> GalleryItem:
    return GalleryItem.model_validate(app, from_attributes=True)


@router.get("", response_model=list[GalleryItem])
async def list_gallery(
    sort: str = "latest",
    tag: str | None = None,
    limit: int = 30,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> list[GalleryItem]:
    apps = await CommunityRepository(db).list_public(sort=sort, tag=tag, limit=limit, offset=offset)
    return [_to_item(app) for app in apps]


@router.get("/{app_id}", response_model=GalleryDetail)
async def gallery_detail(
    app_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: UserORM | None = Depends(get_optional_user),
) -> GalleryDetail:
    repo = CommunityRepository(db)
    app = await repo.get_public(app_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artwork not found")
    await repo.increment_view(app)
    comments = await repo.list_comments(app_id)
    liked = await repo.has_liked(user.id, app_id) if user else False
    detail = GalleryDetail.model_validate(app, from_attributes=True)
    detail.liked = liked
    detail.comments = [CommentResponse.model_validate(c, from_attributes=True) for c in comments]
    return detail


@router.post("/{app_id}/like", response_model=GalleryDetail)
async def like_artwork(
    app_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: UserORM = Depends(get_current_user),
) -> GalleryDetail:
    repo = CommunityRepository(db)
    app = await repo.get_public(app_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artwork not found")
    await repo.add_like(user.id, app)
    return await gallery_detail(app_id, db, user)


@router.delete("/{app_id}/like", response_model=GalleryDetail)
async def unlike_artwork(
    app_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: UserORM = Depends(get_current_user),
) -> GalleryDetail:
    repo = CommunityRepository(db)
    app = await repo.get_public(app_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artwork not found")
    await repo.remove_like(user.id, app)
    return await gallery_detail(app_id, db, user)


@router.post("/{app_id}/comments", response_model=CommentResponse)
async def add_comment(
    app_id: UUID,
    payload: CreateCommentRequest,
    db: AsyncSession = Depends(get_db),
    user: UserORM = Depends(get_current_user),
) -> CommentResponse:
    repo = CommunityRepository(db)
    app = await repo.get_public(app_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artwork not found")
    comment = await repo.add_comment(user.id, app, payload.content)
    return CommentResponse.model_validate(comment, from_attributes=True)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: UserORM = Depends(get_current_user),
) -> None:
    ok = await CommunityRepository(db).delete_comment(comment_id, user.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")


# --- user profiles ---
profiles_router = APIRouter()


@profiles_router.get("/{user_id}/profile", response_model=ProfileResponse)
async def user_profile(user_id: UUID, db: AsyncSession = Depends(get_db)) -> ProfileResponse:
    user = await UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    repo = CommunityRepository(db)
    profile = await repo.get_profile(user_id)
    apps = await repo.list_by_owner_public(user_id)
    return ProfileResponse(
        user_id=user_id,
        display_name=profile.display_name if profile else None,
        bio=profile.bio if profile else None,
        avatar_url=profile.avatar_url if profile else None,
        public_app_count=len(apps),
        apps=[_to_item(app) for app in apps],
    )


@profiles_router.put("/me/profile", response_model=ProfileResponse)
async def update_my_profile(
    payload: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    user: UserORM = Depends(get_current_user),
) -> ProfileResponse:
    repo = CommunityRepository(db)
    await repo.upsert_profile(user.id, payload.model_dump(exclude_unset=True))
    return await user_profile(user.id, db)
