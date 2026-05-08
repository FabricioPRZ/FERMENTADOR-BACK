from src.services.users.infrastructure.adapters.MySQL import UserRepository
from src.core.database import AsyncSessionLocal


def get_user_repository() -> UserRepository:
    return UserRepository(AsyncSessionLocal)