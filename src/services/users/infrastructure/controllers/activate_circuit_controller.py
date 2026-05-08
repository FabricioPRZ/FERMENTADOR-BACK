from src.services.users.application.usecase.activate_my_circuit_use_case import ActivateMyCircuitUseCase
from src.services.users.infrastructure.adapters.MySQL import UserRepository
from src.services.circuits.infrastructure.adapters.MySQL import CircuitRepository
from src.services.users.domain.dto.activate_circuit_schema import ActivateCircuitRequest, ActivateCircuitResponse
from src.core.database import AsyncSessionLocal


async def activate_my_circuit(user_id: int, body: ActivateCircuitRequest) -> ActivateCircuitResponse:
    repo = UserRepository(AsyncSessionLocal)
    circuit_repo = CircuitRepository(AsyncSessionLocal)
    return await ActivateMyCircuitUseCase(repo, circuit_repo).execute(
        user_id=user_id,
        activation_code=body.activation_code,
    )
