from modules.users.domain.entities.entities import User
from modules.users.domain.repository import IUserRepository
from core.security import hash_password
from core.exceptions import UserNotFoundException, UserAlreadyExistsException

ROLE_IDS = {"admin": 1, "profesor": 2, "estudiante": 3}


class UpdateUserUseCase:

    def __init__(self, repository: IUserRepository):
        self._repo = repository

    async def execute(
        self,
        user_id:   int,
        name:      str | None = None,
        last_name: str | None = None,
        email:     str | None = None,
        password:  str | None = None,
        role:      str | None = None,
    ) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        if email and email != user.email:
            existing = await self._repo.get_by_email(email)
            if existing:
                raise UserAlreadyExistsException()

        user.name      = name      or user.name
        user.last_name = last_name or user.last_name
        user.email     = email     or user.email
        user.password  = hash_password(password) if password else user.password
        user.role_id   = ROLE_IDS.get(role, user.role_id) if role else user.role_id

        return await self._repo.update(user)