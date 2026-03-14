from fastapi import APIRouter
from modules.auth.domain.dto.schemas import (
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    TokenResponse,
    AccessTokenResponse,
    RegisterResponse,
)
from modules.auth.infrastructure.controllers.auth_controller import (
    login,
    register,
    refresh_token,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
    summary="Registrar nuevo administrador",
)
async def register_route(body: RegisterRequest):
    return await register(body)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
)
async def login_route(body: LoginRequest):
    return await login(body)


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Refrescar access token",
)
async def refresh_route(body: RefreshTokenRequest):
    return await refresh_token(body)