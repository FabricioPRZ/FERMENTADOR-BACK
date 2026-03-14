from modules.users.domain.repository import IUserRepository
from core.exceptions import UserNotFoundException


class DeleteUserUseCase:

    def __init__(self, repository: IUserRepository):
        self._repo = repository

    async def execute(self, user_id: int) -> None:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        await self._repo.delete(user_id)