from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import AnnouncementORM, GeneratedAppORM, TaskORM, UserORM


class AdminRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_users(self, limit: int = 100, offset: int = 0) -> list[UserORM]:
        result = await self.db.execute(
            select(UserORM).order_by(UserORM.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def set_user_admin(self, user_id: UUID, is_admin: bool) -> UserORM | None:
        user = await self.db.get(UserORM, user_id)
        if user:
            user.is_admin = is_admin
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def adjust_credits(self, user_id: UUID, delta: int) -> UserORM | None:
        user = await self.db.get(UserORM, user_id)
        if user:
            user.credits = max(0, user.credits + delta)
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def list_apps(
        self, status: str | None = None, limit: int = 100, offset: int = 0
    ) -> list[GeneratedAppORM]:
        query = select(GeneratedAppORM).order_by(GeneratedAppORM.created_at.desc())
        if status:
            query = query.where(GeneratedAppORM.status == status)
        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def moderate_app(self, app_id: UUID, action: str) -> GeneratedAppORM | None:
        app = await self.db.get(GeneratedAppORM, app_id)
        if not app:
            return None
        if action == "approve":
            app.status = "approved"
        elif action == "reject":
            app.status = "rejected"
            app.visibility = "private"
        await self.db.commit()
        await self.db.refresh(app)
        return app

    async def list_tasks(self, limit: int = 100, offset: int = 0) -> list[TaskORM]:
        result = await self.db.execute(
            select(TaskORM).order_by(TaskORM.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def stats(self) -> dict:
        users = await self.db.scalar(select(func.count()).select_from(UserORM))
        apps = await self.db.scalar(select(func.count()).select_from(GeneratedAppORM))
        tasks = await self.db.scalar(select(func.count()).select_from(TaskORM))
        return {"users": int(users or 0), "apps": int(apps or 0), "tasks": int(tasks or 0)}

    # announcements
    async def list_announcements(self) -> list[AnnouncementORM]:
        result = await self.db.execute(
            select(AnnouncementORM).order_by(AnnouncementORM.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_announcement(self, title: str, body: str) -> AnnouncementORM:
        item = AnnouncementORM(title=title, body=body)
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete_announcement(self, announcement_id: UUID) -> bool:
        item = await self.db.get(AnnouncementORM, announcement_id)
        if not item:
            return False
        await self.db.delete(item)
        await self.db.commit()
        return True
