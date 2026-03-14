from abc import ABC, abstractmethod
from modules.users.domain.entities.entities import User


class IUserRepository(ABC):

    @abstractmethod
    async def get_all(self) -> list[User]:
        ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        ...

    @abstractmethod
    async def get_created_by(self, creator_id: int) -> list[User]:
        """Retorna todos los usuarios creados por creator_id."""
        ...

    @abstractmethod
    async def create(self, user: User) -> User:
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        ...

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        ...