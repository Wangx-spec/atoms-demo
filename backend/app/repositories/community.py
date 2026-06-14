from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import (
    GalleryCommentORM,
    GeneratedAppORM,
    LikeORM,
    UserProfileORM,
)


class CommunityRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_public(
        self, sort: str = "latest", tag: str | None = None, limit: int = 30, offset: int = 0
    ) -> list[GeneratedAppORM]:
        query = select(GeneratedAppORM).where(GeneratedAppORM.visibility == "public")
        if tag:
            query = query.where(GeneratedAppORM.tags.ilike(f"%{tag}%"))
        if sort == "popular":
            query = query.order_by(GeneratedAppORM.like_count.desc(), GeneratedAppORM.view_count.desc())
        else:
            query = query.order_by(GeneratedAppORM.published_at.desc().nullslast())
        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_ids(self, ids: list[UUID]) -> list[GeneratedAppORM]:
        if not ids:
            return []
        result = await self.db.execute(
            select(GeneratedAppORM).where(
                GeneratedAppORM.id.in_(ids), GeneratedAppORM.visibility == "public"
            )
        )
        by_id = {app.id: app for app in result.scalars().all()}
        return [by_id[i] for i in ids if i in by_id]

    async def text_search(self, query: str, limit: int = 20) -> list[GeneratedAppORM]:
        like = f"%{query}%"
        result = await self.db.execute(
            select(GeneratedAppORM)
            .where(
                GeneratedAppORM.visibility == "public",
                (GeneratedAppORM.prompt.ilike(like))
                | (GeneratedAppORM.title.ilike(like))
                | (GeneratedAppORM.tags.ilike(like)),
            )
            .order_by(GeneratedAppORM.like_count.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_public(self, app_id: UUID) -> GeneratedAppORM | None:
        app = await self.db.get(GeneratedAppORM, app_id)
        if app and app.visibility == "public":
            return app
        return None

    async def increment_view(self, app: GeneratedAppORM) -> None:
        app.view_count += 1
        await self.db.commit()

    async def list_by_owner_public(self, user_id: UUID) -> list[GeneratedAppORM]:
        result = await self.db.execute(
            select(GeneratedAppORM)
            .where(GeneratedAppORM.user_id == user_id, GeneratedAppORM.visibility == "public")
            .order_by(GeneratedAppORM.published_at.desc().nullslast())
        )
        return list(result.scalars().all())

    # --- likes ---
    async def has_liked(self, user_id: UUID, app_id: UUID) -> bool:
        result = await self.db.execute(
            select(LikeORM).where(LikeORM.user_id == user_id, LikeORM.app_id == app_id)
        )
        return result.scalar_one_or_none() is not None

    async def add_like(self, user_id: UUID, app: GeneratedAppORM) -> None:
        if await self.has_liked(user_id, app.id):
            return
        self.db.add(LikeORM(user_id=user_id, app_id=app.id))
        app.like_count += 1
        await self.db.commit()

    async def remove_like(self, user_id: UUID, app: GeneratedAppORM) -> None:
        result = await self.db.execute(
            delete(LikeORM).where(LikeORM.user_id == user_id, LikeORM.app_id == app.id)
        )
        if result.rowcount:
            app.like_count = max(0, app.like_count - 1)
        await self.db.commit()

    # --- comments ---
    async def add_comment(self, user_id: UUID, app: GeneratedAppORM, content: str) -> GalleryCommentORM:
        comment = GalleryCommentORM(user_id=user_id, app_id=app.id, content=content)
        self.db.add(comment)
        app.comment_count += 1
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def list_comments(self, app_id: UUID) -> list[GalleryCommentORM]:
        result = await self.db.execute(
            select(GalleryCommentORM)
            .where(GalleryCommentORM.app_id == app_id)
            .order_by(GalleryCommentORM.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_comment(self, comment_id: UUID, user_id: UUID) -> bool:
        comment = await self.db.get(GalleryCommentORM, comment_id)
        if not comment or comment.user_id != user_id:
            return False
        app = await self.db.get(GeneratedAppORM, comment.app_id)
        await self.db.delete(comment)
        if app:
            app.comment_count = max(0, app.comment_count - 1)
        await self.db.commit()
        return True

    # --- profiles ---
    async def get_profile(self, user_id: UUID) -> UserProfileORM | None:
        return await self.db.get(UserProfileORM, user_id)

    async def upsert_profile(self, user_id: UUID, data: dict) -> UserProfileORM:
        profile = await self.db.get(UserProfileORM, user_id)
        if not profile:
            profile = UserProfileORM(user_id=user_id, **data)
            self.db.add(profile)
        else:
            for key, value in data.items():
                setattr(profile, key, value)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def count_public_apps(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(GeneratedAppORM)
            .where(GeneratedAppORM.user_id == user_id, GeneratedAppORM.visibility == "public")
        )
        return int(result.scalar_one())
