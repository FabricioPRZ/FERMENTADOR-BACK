from fastapi import APIRouter, Depends
from modules.users.domain.dto.schemas import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
    ActivateCircuitRequest,
    ActivateCircuitResponse,
)
from modules.users.infrastructure.controllers import user_controller
from core.dependencies import require_admin, require_admin_or_profesor, require_any_role

router = APIRouter()


@router.post(
    "/me/activate",
    response_model=ActivateCircuitResponse,
    summary="Activar mi circuito con código de activación",
)
async def activate_my_circuit(
    body: ActivateCircuitRequest,
    current_user: dict = Depends(require_any_role),
):
    """
    El admin ingresa su activation_code una sola vez.
    - Se asigna el circuit_id a su cuenta de forma permanente.
    - Se devuelve un nuevo access_token con el circuit_id incluido.
    - A partir de aquí puede crear usuarios con ese mismo código
      y estos ya nacen con circuit_id asignado.
    """
    return await user_controller.activate_my_circuit(
        user_id=current_user["user_id"],
        body=body,
    )


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Ver usuarios que yo creé",
)
async def get_all_users(
    current_user: dict = Depends(require_admin_or_profesor),
):
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
    El activation_code determina el circuito al que se asocia el nuevo usuario.
    El nuevo usuario ya nace con circuit_id asignado y no necesita ingresar el código.
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