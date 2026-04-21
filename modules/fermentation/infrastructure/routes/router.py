from fastapi import APIRouter, Depends
from modules.fermentation.domain.dto.schemas import (
    ScheduleFermentationRequest,
    StopFermentationRequest,
    FermentationSessionResponse,
    FermentationReportResponse,
    ReportHistoryResponse,
)
from modules.fermentation.infrastructure.controllers import fermentation_controller
from core.dependencies import require_admin_or_profesor, require_any_role

router = APIRouter()


@router.post(
    "/schedule",
    response_model=FermentationSessionResponse,
    status_code=201,
    summary="Programar fermentación",
)
async def schedule_fermentation(
    body: ScheduleFermentationRequest,
    current_user: dict = Depends(require_admin_or_profesor),
):
    return await fermentation_controller.schedule(body, current_user["user_id"])


@router.post(
    "/{session_id}/start",
    response_model=FermentationSessionResponse,
    summary="Iniciar fermentación",
)
async def start_fermentation(
    session_id: int,
    current_user: dict = Depends(require_admin_or_profesor),
):
    return await fermentation_controller.start(session_id)


@router.post(
    "/{session_id}/stop",
    response_model=FermentationSessionResponse,
    summary="Detener fermentación",
)
async def stop_fermentation(
    session_id: int,
    body: StopFermentationRequest,
    current_user: dict = Depends(require_admin_or_profesor),
):
    return await fermentation_controller.stop(session_id, body, current_user["user_id"])


@router.get(
    "/{session_id}/report",
    response_model=FermentationReportResponse,
    summary="Obtener reporte",
)
async def get_report(
    session_id: int,
    current_user: dict = Depends(require_any_role),
):
    return await fermentation_controller.get_report(session_id, current_user["user_id"])


@router.get(
    "/history",
    response_model=list[ReportHistoryResponse],
    summary="Historial de reportes del usuario",
)
async def get_report_history(
    current_user: dict = Depends(require_any_role),
):
    return await fermentation_controller.get_report_history(current_user["user_id"])

@router.get(
    "/active",
    response_model=FermentationSessionResponse | None,
    summary="Sesion activa del circuito del usuario",
)
async def get_active_session(
    current_user: dict = Depends(require_any_role),
):
    return await fermentation_controller.get_active(
        current_user.get("circuit_id"),
        current_user.get("user_id"),
    )
