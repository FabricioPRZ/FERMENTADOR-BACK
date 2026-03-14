from datetime import datetime
from fastapi import APIRouter, Depends, Query
from modules.sensors.domain.dto.schemas import SensorReadingResponse, SensorHistoryResponse
from modules.sensors.infrastructure.controllers import sensor_controller
from core.dependencies import require_any_role

router = APIRouter()


@router.get(
    "/{circuit_id}/{sensor_type}/history",
    response_model=SensorHistoryResponse,
    summary="Historial de lecturas de un sensor",
)
async def get_sensor_history(
    circuit_id:  int,
    sensor_type: str,
    session_id:  int | None = Query(default=None),
    from_dt:     datetime | None = Query(default=None),
    to_dt:       datetime | None = Query(default=None),
    current_user: dict = Depends(require_any_role),
):
    return await sensor_controller.get_history(
        circuit_id=circuit_id,
        sensor_type=sensor_type,
        session_id=session_id,
        from_dt=from_dt,
        to_dt=to_dt,
    )


@router.get(
    "/{circuit_id}/{sensor_type}/latest",
    response_model=SensorReadingResponse | None,
    summary="Última lectura de un sensor",
)
async def get_latest_reading(
    circuit_id:  int,
    sensor_type: str,
    current_user: dict = Depends(require_any_role),
):
    return await sensor_controller.get_latest(circuit_id, sensor_type)