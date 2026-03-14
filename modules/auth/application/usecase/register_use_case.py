from modules.auth.domain.repository import IAuthRepository
from core.security import hash_password
from core.exceptions import EmailAlreadyExistsException

ADMIN_ROLE_ID = 1


class RegisterUseCase:

    def __init__(self, repository: IAuthRepository):
        self._repo = repository

    async def execute(
        self,
        name:      str,
        last_name: str,
        email:     str,
        password:  str,
    ) -> dict:
        existing = await self._repo.get_user_by_email(email)
        if existing:
            raise EmailAlreadyExistsException()

        hashed = hash_password(password)

        # El admin se registra sin circuito asignado todavía.
        # Su circuit_id se asigna cuando crea un usuario con un activation_code.
        user = await self._repo.create_user(
            name=name,
            last_name=last_name,
            email=email,
            password=hashed,
            role_id=ADMIN_ROLE_ID,
            circuit_id=None,
        )

        return {
            "id":        user.id,
            "name":      user.name,
            "last_name": user.last_name,
            "email":     user.email,
            "role":      user.role.name if user.role else "admin",
        }