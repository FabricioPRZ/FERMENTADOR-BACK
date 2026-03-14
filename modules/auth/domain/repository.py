from abc import ABC, abstractmethod
from modules.auth.domain.entities.entities import User


class IAuthRepository(ABC):

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        ...

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User | None:
        ...

    @abstractmethod
    async def create_user(
        self,
        name:       str,
        last_name:  str,
        email:      str,
        password:   str,
        role_id:    int,
        circuit_id: int | None = None,
    ) -> User:
        ...