from modules.users.infrastructure.adapters.MySQL import UserRepository
from core.database import AsyncSessionLocal


def get_user_repository() -> UserRepository:
    return UserRepository(AsyncSessionLocal)