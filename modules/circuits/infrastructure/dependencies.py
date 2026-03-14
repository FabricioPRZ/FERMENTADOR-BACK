from modules.circuits.infrastructure.adapters.MySQL import CircuitRepository
from core.database import AsyncSessionLocal


def get_circuit_repository() -> CircuitRepository:
    return CircuitRepository(AsyncSessionLocal)