from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.db import UserORM
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse


def to_user_response(user: UserORM) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        credits=user.credits,
        avatar_url=user.avatar_url,
        is_admin=bool(getattr(user, "is_admin", False)),
    )


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.users = UserRepository(db)

    async def register(self, payload: RegisterRequest) -> TokenResponse:
        if await self.users.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        user = await self.users.create(
            email=payload.email,
            password_hash=hash_password(payload.password),
        )
        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token, user=to_user_response(user))

    async def login(self, payload: LoginRequest) -> TokenResponse:
        user = await self.users.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token, user=to_user_response(user))
