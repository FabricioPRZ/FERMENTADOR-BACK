from modules.sensors.domain.entities.entities import SensorReading
from modules.sensors.domain.repository import ISensorRepository
from core.websocket.websocket_manager import ws_manager
from core.websocket.schemas import SensorDataMessage, SensorDeactivatedMessage
from datetime import datetime, timezone


class SaveReadingUseCase:

    def __init__(self, repository: ISensorRepository):
        self._repo = repository

    async def execute(
        self,
        circuit_id:  int,
        sensor_type: str,
        value:       float,
        session_id:  int | None = None,
    ) -> SensorReading:
        """Persiste la lectura y hace broadcast al front vía WS."""
        reading = await self._repo.save_reading(
            circuit_id=circuit_id,
            sensor_type=sensor_type,
            value=value,
            session_id=session_id,
        )

        if ws_manager.is_circuit_connected(circuit_id):
            msg = SensorDataMessage(
                circuit_id=circuit_id,
                sensor_type=sensor_type,
                value=value,
                session_id=session_id,
                timestamp=reading.timestamp or datetime.now(timezone.utc),
            )
            await ws_manager.broadcast_sensor(circuit_id, msg)

        return reading

    async def execute_deactivation(
        self,
        circuit_id:  int,
        sensor_type: str,
        session_id:  int,
        value:       float,
    ) -> None:
        """Notifica al módulo de fermentación que el sensor fue desactivado."""
        from modules.fermentation.infrastructure.adapters.MySQL import FermentationRepository
        from core.database import AsyncSessionLocal

        now = datetime.now(timezone.utc)

        fermentation_repo = FermentationRepository(AsyncSessionLocal)
        await fermentation_repo.update_sensor_deactivation(
            session_id=session_id,
            sensor_type=sensor_type,
            last_reading=value,
            deactivated_at=now,
        )

        if ws_manager.is_circuit_connected(circuit_id):
            msg = SensorDeactivatedMessage(
                circuit_id=circuit_id,
                sensor_type=sensor_type,
                session_id=session_id,
                deactivated_at=now,
            )
            await ws_manager.broadcast_sensor(circuit_id, msg)