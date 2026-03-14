from fastapi import APIRouter, Depends
from modules.formula.domain.dto.schemas import UpdateFormulaRequest, FormulaResponse
from modules.formula.infrastructure.controllers import formula_controller
from core.dependencies import get_current_user, require_admin_or_profesor

router = APIRouter()


@router.get(
    "/active",
    response_model=FormulaResponse,
    summary="Obtener fórmula activa",
)
async def get_active_formula(
    current_user: dict = Depends(get_current_user),
):
    return await formula_controller.get_active()


@router.get(
    "/",
    response_model=list[FormulaResponse],
    summary="Listar todas las fórmulas",
)
async def get_all_formulas(
    current_user: dict = Depends(get_current_user),
):
    return await formula_controller.get_all()


@router.get(
    "/{formula_id}",
    response_model=FormulaResponse,
    summary="Obtener fórmula por ID",
)
async def get_formula(
    formula_id: int,
    current_user: dict = Depends(get_current_user),
):
    return await formula_controller.get_by_id(formula_id)


@router.put(
    "/{formula_id}",
    response_model=FormulaResponse,
    summary="Editar fórmula",
)
async def update_formula(
    formula_id: int,
    body: UpdateFormulaRequest,
    current_user: dict = Depends(require_admin_or_profesor),
):
    return await formula_controller.update(formula_id, body, current_user["user_id"])


@router.patch(
    "/{formula_id}/activate",
    response_model=FormulaResponse,
    summary="Cambiar fórmula activa",
)
async def activate_formula(
    formula_id: int,
    current_user: dict = Depends(require_admin_or_profesor),
):
    return await formula_controller.activate(formula_id, current_user["user_id"])