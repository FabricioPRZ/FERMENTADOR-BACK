from modules.fermentation.application.usecase.schedule_fermentation_use_case import ScheduleFermentationUseCase
from modules.fermentation.application.usecase.start_fermentation_use_case import StartFermentationUseCase
from modules.fermentation.application.usecase.stop_fermentation_use_case import StopFermentationUseCase
from modules.fermentation.application.usecase.get_report_use_case import GetReportUseCase
from modules.fermentation.application.usecase.get_report_history_use_case import GetReportHistoryUseCase
from modules.fermentation.infrastructure.adapters.MySQL import FermentationRepository
from modules.sensors.infrastructure.adapters.MySQL import SensorRepository
from modules.circuits.infrastructure.adapters.MySQL import CircuitRepository
from modules.fermentation.domain.dto.schemas import (
    ScheduleFermentationRequest,
    StopFermentationRequest,
    FermentationSessionResponse,
    FermentationReportResponse,
    ReportHistoryResponse,
)
from core.database import AsyncSessionLocal
from core.exceptions import FermentationSessionNotFoundException


def _repo():
    return FermentationRepository(AsyncSessionLocal)

def _sensor_repo():
    return SensorRepository(AsyncSessionLocal)

def _circuit_repo():
    return CircuitRepository(AsyncSessionLocal)


def _session_to_response(session) -> FermentationSessionResponse:
    return FermentationSessionResponse(
        id=session.id,
        circuit_id=session.circuit_id,
        user_id=session.user_id,
        formula_id=session.formula_id,
        scheduled_start=session.scheduled_start,
        scheduled_end=session.scheduled_end,
        actual_start=session.actual_start,
        actual_end=session.actual_end,
        status=session.status,
        interrupted_by=session.interrupted_by,
        created_at=session.created_at,
    )


async def schedule(
    body: ScheduleFermentationRequest,
    user_id: int,
) -> FermentationSessionResponse:
    session = await ScheduleFermentationUseCase(_repo()).execute(
        circuit_id=body.circuit_id,
        user_id=user_id,
        scheduled_start=body.scheduled_start,
        scheduled_end=body.scheduled_end,
        initial_sugar=body.initial_sugar,
    )
    return _session_to_response(session)


async def start(session_id: int) -> FermentationSessionResponse:
    fermentation_repo = _repo()
    session_data = await fermentation_repo.get_session_by_id(session_id)
    if not session_data:
        raise FermentationSessionNotFoundException()

    circuit = await _circuit_repo().get_by_id(session_data.circuit_id)
    session = await StartFermentationUseCase(fermentation_repo, _sensor_repo()).execute(
        session_id=session_id,
        circuit=circuit,
    )
    return _session_to_response(session)


async def stop(
    session_id: int,
    body: StopFermentationRequest,
    user_id: int,
) -> FermentationSessionResponse:
    fermentation_repo = _repo()
    session_data = await fermentation_repo.get_session_by_id(session_id)
    if not session_data:
        raise FermentationSessionNotFoundException()

    circuit = await _circuit_repo().get_by_id(session_data.circuit_id)
    session = await StopFermentationUseCase(fermentation_repo, _sensor_repo()).execute(
        session_id=session_id,
        circuit=circuit,
        interrupted_by=user_id if body.interrupted else None,
    )
    return _session_to_response(session)


async def get_report(session_id: int, user_id: int) -> FermentationReportResponse:
    return await GetReportUseCase(_repo()).execute(session_id, user_id)


async def get_report_history(user_id: int) -> list[ReportHistoryResponse]:
    return await GetReportHistoryUseCase(_repo()).execute(user_id)