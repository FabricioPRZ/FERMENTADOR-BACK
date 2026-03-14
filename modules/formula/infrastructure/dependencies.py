from modules.formula.infrastructure.adapters.MySQL import FormulaRepository
from core.database import AsyncSessionLocal


def get_formula_repository() -> FormulaRepository:
    return FormulaRepository(AsyncSessionLocal)