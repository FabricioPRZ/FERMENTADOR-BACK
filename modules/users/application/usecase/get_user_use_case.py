from modules.users.domain.entities.entities import User
from modules.users.domain.repository import IUserRepository
from core.exceptions import UserNotFoundException


class GetUserUseCase:

    def __init__(self, repository: IUserRepository):
        self._repo = repository

    async def get_all(self, requester_id: int, requester_role: str) -> list[User]:
        """
        - admin: ve todos los usuarios que él creó (created_by = requester_id)
        - profesor: ve todos los usuarios que él creó (created_by = requester_id)
        Solo un superadmin técnico (sin restricción) vería get_all completo,
        pero en este sistema admin y profesor siempre ven solo sus creados.
        """
        return await self._repo.get_created_by(requester_id)

    async def get_by_id(self, user_id: int) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return user