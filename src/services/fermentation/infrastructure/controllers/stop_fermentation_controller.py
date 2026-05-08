from src.services.fermentation.application.usecase.stop_fermentation_use_case import StopFermentationUseCase
from src.services.fermentation.infrastructure.adapters.MySQL import FermentationRepository
from src.services.sensors.infrastructure.adapters.MySQL import SensorRepository
from src.services.circuits.infrastructure.adapters.MySQL import CircuitRepository
from src.services.fermentation.domain.dto.stop_fermentation_schema import StopFermentationRequest
from src.services.fermentation.domain.dto.fermentation_session_schema import FermentationSessionResponse
from src.core.database import AsyncSessionLocal
from src.core.exceptions import FermentationSessionNotFoundException


async def stop(session_id: int, body: StopFermentationRequest, user_id: int) -> FermentationSessionResponse:
    fermentation_repo = FermentationRepository(AsyncSessionLocal)
    session_data = await fermentation_repo.get_session_by_id(session_id)
    if not session_data:
        raise FermentationSessionNotFoundException()

    circuit = await CircuitRepository(AsyncSessionLocal).get_by_id(session_data.circuit_id)
    session = await StopFermentationUseCase(fermentation_repo, SensorRepository(AsyncSessionLocal)).execute(
        session_id     = session_id,
        circuit        = circuit,
        interrupted_by = user_id if body.interrupted else None,
    )
    return FermentationSessionResponse.from_entity(session)
