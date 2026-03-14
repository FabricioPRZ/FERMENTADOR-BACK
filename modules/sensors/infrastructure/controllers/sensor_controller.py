from datetime import datetime
from modules.sensors.application.usecase.get_history_use_case import GetHistoryUseCase
from modules.sensors.infrastructure.adapters.MySQL import SensorRepository
from modules.sensors.domain.dto.schemas import SensorReadingResponse, SensorHistoryResponse
from core.database import AsyncSessionLocal


def _repo():
    return SensorRepository(AsyncSessionLocal)


def _to_reading_response(reading) -> SensorReadingResponse:
    return SensorReadingResponse(
        id=reading.id,
        circuit_id=reading.circuit_id,
        sensor_type=reading.sensor_type,
        value=reading.value,
        session_id=reading.session_id,
        timestamp=reading.timestamp,
    )


async def get_history(
    circuit_id:  int,
    sensor_type: str,
    session_id:  int | None = None,
    from_dt:     datetime | None = None,
    to_dt:       datetime | None = None,
) -> SensorHistoryResponse:
    readings = await GetHistoryUseCase(_repo()).execute(
        circuit_id=circuit_id,
        sensor_type=sensor_type,
        session_id=session_id,
        from_dt=from_dt,
        to_dt=to_dt,
    )
    return SensorHistoryResponse(
        circuit_id=circuit_id,
        sensor_type=sensor_type,
        readings=[_to_reading_response(r) for r in readings],
    )


async def get_latest(
    circuit_id:  int,
    sensor_type: str,
) -> SensorReadingResponse | None:
    reading = await _repo().get_latest_reading(circuit_id, sensor_type)
    return _to_reading_response(reading) if reading else None