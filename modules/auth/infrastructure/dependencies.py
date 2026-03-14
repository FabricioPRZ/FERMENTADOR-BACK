from modules.auth.infrastructure.adapters.MySQL import AuthRepository
from core.database import AsyncSessionLocal


def get_auth_repository() -> AuthRepository:
    return AuthRepository(AsyncSessionLocal)