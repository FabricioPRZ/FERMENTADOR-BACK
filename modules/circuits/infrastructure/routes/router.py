from fastapi import APIRouter, Depends
from modules.circuits.domain.dto.schemas import (
    CircuitResponse,
    CreateCircuitResponse,
)
from modules.circuits.infrastructure.controllers import circuit_controller
from core.dependencies import require_any_role, require_admin_or_profesor
from core.exceptions import CircuitNotFoundException

router = APIRouter()


@router.post(
    "/",
    response_model=CreateCircuitResponse,
    status_code=201,
    summary="Crear nuevo circuito (solo equipo de instalación)",
)
async def create_circuit():
    return await circuit_controller.create()


@router.get(
    "/me",
    response_model=CircuitResponse,
    summary="Ver mi circuito",
)
async def get_my_circuit(
    current_user: dict = Depends(require_any_role),
):
    """
    Retorna el circuito asociado al usuario autenticado.
    El circuit_id viene del payload JWT del usuario.
    """
    circuit_id = current_user.get("circuit_id")
    return await circuit_controller.get_my_circuit(circuit_id)


@router.get(
    "/{circuit_id}",
    response_model=CircuitResponse,
    summary="Ver circuito por ID (admin y profesor)",
)
async def get_circuit(
    circuit_id: int,
    current_user: dict = Depends(require_admin_or_profesor),
):
    return await circuit_controller.get_by_id(circuit_id)