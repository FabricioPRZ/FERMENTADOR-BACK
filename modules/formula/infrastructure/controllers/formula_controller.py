from modules.formula.application.usecase.get_formula_use_case import GetFormulaUseCase
from modules.formula.application.usecase.update_formula_use_case import UpdateFormulaUseCase
from modules.formula.infrastructure.adapters.MySQL import FormulaRepository
from modules.formula.domain.dto.schemas import UpdateFormulaRequest, FormulaResponse
from core.database import AsyncSessionLocal


def _repo():
    return FormulaRepository(AsyncSessionLocal)


def _to_response(formula) -> FormulaResponse:
    return FormulaResponse(
        id=formula.id,
        name=formula.name,
        conversion_factor=formula.conversion_factor,
        description=formula.description,
        is_active=formula.is_active,
        updated_by=formula.updated_by,
        updated_at=formula.updated_at,
        created_at=formula.created_at,
    )


async def get_active() -> FormulaResponse:
    formula = await GetFormulaUseCase(_repo()).get_active()
    return _to_response(formula)


async def get_all() -> list[FormulaResponse]:
    formulas = await GetFormulaUseCase(_repo()).get_all()
    return [_to_response(f) for f in formulas]


async def get_by_id(formula_id: int) -> FormulaResponse:
    formula = await GetFormulaUseCase(_repo()).get_by_id(formula_id)
    return _to_response(formula)


async def update(
    formula_id: int,
    body: UpdateFormulaRequest,
    updated_by: int,
) -> FormulaResponse:
    formula = await UpdateFormulaUseCase(_repo()).execute(
        formula_id=formula_id,
        updated_by=updated_by,
        name=body.name,
        conversion_factor=body.conversion_factor,
        description=body.description,
    )
    return _to_response(formula)


async def activate(formula_id: int, updated_by: int) -> FormulaResponse:
    formula = await UpdateFormulaUseCase(_repo()).set_active(
        formula_id=formula_id,
        updated_by=updated_by,
    )
    return _to_response(formula)