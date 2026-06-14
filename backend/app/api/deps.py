from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import async_session
from app.models.db import UserORM
from app.repositories.users import UserRepository


async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> UserORM:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    token = authorization.removeprefix("Bearer ").strip()
    subject = decode_access_token(token)
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await UserRepository(db).get_by_id(UUID(subject))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


async def get_optional_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> UserORM | None:
    """Like get_current_user but returns None instead of raising (for public pages)."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    subject = decode_access_token(authorization.removeprefix("Bearer ").strip())
    if not subject:
        return None
    return await UserRepository(db).get_by_id(UUID(subject))


async def get_admin_user(
    current_user: UserORM = Depends(get_current_user),
) -> UserORM:
    from app.core.config import settings

    is_admin = bool(getattr(current_user, "is_admin", False)) or (
        current_user.email in settings.admin_emails
    )
    if not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return current_user
