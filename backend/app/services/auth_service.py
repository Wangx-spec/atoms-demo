from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.models.entities import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.repository import repository


def to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        credits=user.credits,
        avatar_url=user.avatar_url,
    )


class AuthService:
    def register(self, payload: RegisterRequest) -> TokenResponse:
        if repository.get_user_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        user = repository.add_user(
            User(email=payload.email, password_hash=hash_password(payload.password))
        )
        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token, user=to_user_response(user))

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = repository.get_user_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token, user=to_user_response(user))


auth_service = AuthService()
