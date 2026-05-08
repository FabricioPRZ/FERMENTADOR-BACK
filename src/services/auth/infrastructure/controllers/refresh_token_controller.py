from src.services.auth.application.usecase.refresh_token_use_case import RefreshTokenUseCase
from src.services.auth.infrastructure.adapters.MySQL import AuthRepository
from src.services.auth.domain.dto.refresh_token_schema import RefreshTokenRequest, AccessTokenResponse
from src.core.database import AsyncSessionLocal


async def refresh_token(body: RefreshTokenRequest) -> AccessTokenResponse:
    repo = AuthRepository(AsyncSessionLocal)
    return await RefreshTokenUseCase(repo).execute(body.refresh_token)
