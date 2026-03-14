from fastapi import APIRouter, Depends
from modules.users.domain.dto.schemas import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
)
from modules.users.infrastructure.controllers import user_controller
from core.dependencies import require_admin, require_admin_or_profesor

router = APIRouter()


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Listar mis usuarios (los que yo creé)",
)
async def get_all_users(
    current_user: dict = Depends(require_admin_or_profesor),
):
    """
    Admin: ve todos los usuarios que él creó.
    Profesor: ve todos los usuarios que él creó.
    """
    return await user_controller.get_all(
        requester_id=current_user["user_id"],
        requester_role=current_user["role"],
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario por ID",
)
async def get_user(
    user_id: int,
    current_user: dict = Depends(require_admin_or_profesor),
):
    return await user_controller.get_by_id(user_id)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
    summary="Crear usuario (admin o profesor)",
)
async def create_user(
    body: CreateUserRequest,
    current_user: dict = Depends(require_admin_or_profesor),
):
    """
    Admin puede crear: profesor o estudiante.
    Profesor puede crear: solo estudiante.
    Ambos deben pasar el activation_code del circuito al que se asociará el usuario.
    """
    return await user_controller.create(
        body=body,
        created_by=current_user["user_id"],
        creator_role=current_user["role"],
    )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario (solo admin)",
)
async def update_user(
    user_id: int,
    body: UpdateUserRequest,
    current_user: dict = Depends(require_admin),
):
    return await user_controller.update(user_id, body)


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Eliminar usuario (solo admin)",
)
async def delete_user(
    user_id: int,
    current_user: dict = Depends(require_admin),
):
    await user_controller.delete(user_id)