from modules.auth.application.usecase.login_use_case import LoginUseCase
from modules.auth.application.usecase.refresh_token_use_case import RefreshTokenUseCase
from modules.auth.application.usecase.register_use_case import RegisterUseCase
from modules.auth.infrastructure.adapters.MySQL import AuthRepository
from modules.auth.domain.dto.schemas import (
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    TokenResponse,
    AccessTokenResponse,
    RegisterResponse,
)
from core.database import AsyncSessionLocal


def _repo():
    return AuthRepository(AsyncSessionLocal)


async def login(body: LoginRequest) -> TokenResponse:
    return await LoginUseCase(_repo()).execute(
        email=body.email,
        password=body.password,
    )


async def register(body: RegisterRequest) -> RegisterResponse:
    return await RegisterUseCase(_repo()).execute(
        name=body.name,
        last_name=body.last_name,
        email=body.email,
        password=body.password,
    )


async def refresh_token(body: RefreshTokenRequest) -> AccessTokenResponse:
    return await RefreshTokenUseCase(_repo()).execute(body.refresh_token)