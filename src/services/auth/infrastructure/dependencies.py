from src.services.auth.infrastructure.adapters.MySQL import AuthRepository
from src.core.database import AsyncSessionLocal


def get_auth_repository() -> AuthRepository:
    return AuthRepository(AsyncSessionLocal)