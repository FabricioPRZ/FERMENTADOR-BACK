from modules.users.application.usecase.create_user_use_case import CreateUserUseCase
from modules.users.application.usecase.get_user_use_case import GetUserUseCase
from modules.users.application.usecase.update_user_use_case import UpdateUserUseCase
from modules.users.application.usecase.delete_user_use_case import DeleteUserUseCase
from modules.users.application.usecase.activate_my_circuit_use_case import ActivateMyCircuitUseCase
from modules.users.infrastructure.adapters.MySQL import UserRepository
from modules.circuits.infrastructure.adapters.MySQL import CircuitRepository
from modules.users.domain.dto.schemas import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
    ActivateCircuitRequest,
    ActivateCircuitResponse,
)
from core.database import AsyncSessionLocal


def _repo():
    return UserRepository(AsyncSessionLocal)

def _circuit_repo():
    return CircuitRepository(AsyncSessionLocal)

def _to_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        last_name=user.last_name,
        email=user.email,
        role_id=user.role_id,
        role_name=user.role_name,
        circuit_id=user.circuit_id,
        created_by=user.created_by,
        created_at=user.created_at,
    )


async def get_all(requester_id: int, requester_role: str) -> list[UserResponse]:
    users = await GetUserUseCase(_repo()).get_all(
        requester_id=requester_id,
        requester_role=requester_role,
    )
    return [_to_response(u) for u in users]


async def get_by_id(user_id: int) -> UserResponse:
    user = await GetUserUseCase(_repo()).get_by_id(user_id)
    return _to_response(user)


async def create(
    body:         CreateUserRequest,
    created_by:   int,
    creator_role: str,
) -> UserResponse:
    user = await CreateUserUseCase(_repo(), _circuit_repo()).execute(
        name=body.name,
        last_name=body.last_name,
        email=body.email,
        password=body.password,
        role=body.role,
        created_by=created_by,
        creator_role=creator_role,
        activation_code=body.activation_code,
    )
    return _to_response(user)


async def activate_my_circuit(
    user_id:         int,
    body:            ActivateCircuitRequest,
) -> ActivateCircuitResponse:
    return await ActivateMyCircuitUseCase(_repo(), _circuit_repo()).execute(
        user_id=user_id,
        activation_code=body.activation_code,
    )


async def update(user_id: int, body: UpdateUserRequest) -> UserResponse:
    user = await UpdateUserUseCase(_repo()).execute(
        user_id=user_id,
        name=body.name,
        last_name=body.last_name,
        email=body.email,
        password=body.password,
        role=body.role,
    )
    return _to_response(user)


async def delete(user_id: int) -> None:
    await DeleteUserUseCase(_repo()).execute(user_id)