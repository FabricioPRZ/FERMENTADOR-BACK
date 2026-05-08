from src.services.fermentation.application.usecase.start_fermentation_use_case import StartFermentationUseCase
from src.services.fermentation.infrastructure.adapters.MySQL import FermentationRepository
from src.services.sensors.infrastructure.adapters.MySQL import SensorRepository
from src.services.circuits.infrastructure.adapters.MySQL import CircuitRepository
from src.services.fermentation.domain.dto.fermentation_session_schema import FermentationSessionResponse
from src.core.database import AsyncSessionLocal
from src.core.exceptions import FermentationSessionNotFoundException


async def start(session_id: int) -> FermentationSessionResponse:
    fermentation_repo = FermentationRepository(AsyncSessionLocal)
    session_data = await fermentation_repo.get_session_by_id(session_id)
    if not session_data:
        raise FermentationSessionNotFoundException()

    circuit = await CircuitRepository(AsyncSessionLocal).get_by_id(session_data.circuit_id)
    session = await StartFermentationUseCase(fermentation_repo, SensorRepository(AsyncSessionLocal)).execute(
        session_id = session_id,
        circuit    = circuit,
    )
    return FermentationSessionResponse.from_entity(session)
