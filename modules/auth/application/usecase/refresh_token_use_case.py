from modules.auth.domain.repository import IAuthRepository
from core.security import decode_token, create_access_token
from core.exceptions import TokenInvalidException, UserNotFoundException


class RefreshTokenUseCase:

    def __init__(self, repository: IAuthRepository):
        self._repo = repository

    async def execute(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)

        user_id = payload.get("sub")
        if not user_id:
            raise TokenInvalidException()

        user = await self._repo.get_user_by_id(int(user_id))
        if not user:
            raise UserNotFoundException()

        return {
            "access_token": create_access_token({
                "sub":        str(user.id),
                "role":       user.role.name if user.role else "estudiante",
                "circuit_id": user.circuit_id,
            }),
            "token_type": "bearer",
        }