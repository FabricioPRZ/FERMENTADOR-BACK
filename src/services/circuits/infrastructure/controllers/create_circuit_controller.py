from src.services.circuits.application.usecase.create_circuit_use_case import CreateCircuitUseCase
from src.services.circuits.infrastructure.adapters.MySQL import CircuitRepository
from src.services.circuits.domain.dto.create_circuit_schema import CreateCircuitResponse
from src.core.database import AsyncSessionLocal


async def create() -> CreateCircuitResponse:
    repo = CircuitRepository(AsyncSessionLocal)
    circuit = await CreateCircuitUseCase(repo).execute()
    return CreateCircuitResponse(
        id=circuit.id,
        activation_code=circuit.activation_code,
        created_at=circuit.created_at,
    )
