from src.services.users.application.usecase.get_user_use_case import GetUserUseCase
from src.services.users.infrastructure.adapters.MySQL import UserRepository
from src.services.users.domain.dto.user_schema import UserResponse
from src.core.database import AsyncSessionLocal


async def get_by_id(user_id: int) -> UserResponse:
    repo = UserRepository(AsyncSessionLocal)
    user = await GetUserUseCase(repo).get_by_id(user_id)
    return UserResponse.from_entity(user)
