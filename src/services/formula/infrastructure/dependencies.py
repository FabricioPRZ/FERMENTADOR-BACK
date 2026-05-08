from src.services.formula.infrastructure.adapters.MySQL import FormulaRepository
from src.core.database import AsyncSessionLocal


def get_formula_repository() -> FormulaRepository:
    return FormulaRepository(AsyncSessionLocal)