from fastapi import APIRouter

from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import auth_service

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(payload: RegisterRequest) -> TokenResponse:
    return auth_service.register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    return auth_service.login(payload)
