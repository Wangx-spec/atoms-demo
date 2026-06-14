from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator


MAX_BCRYPT_PASSWORD_BYTES = 72


def validate_bcrypt_password(value: str) -> str:
    if len(value.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES:
        raise ValueError("密码过长，bcrypt 最多支持 72 bytes，请使用更短的密码")
    return value


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_must_fit_bcrypt(cls, value: str) -> str:
        return validate_bcrypt_password(value)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_must_fit_bcrypt(cls, value: str) -> str:
        return validate_bcrypt_password(value)


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    credits: int
    avatar_url: str | None = None
    is_admin: bool = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
