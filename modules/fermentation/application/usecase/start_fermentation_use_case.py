from datetime import datetime, timezone
from modules.fermentation.domain.entities.entities import FermentationSession
from modules.fermentation.domain.repository import IFermentationRepository
from modules.sensors.domain.repository import ISensorRepository
from core.threads.sensor_thread_manager import thread_manager
from core.exceptions import (
    FermentationSessionNotFoundException,
    FermentationAlreadyRunningException,
    BadRequestException,
)


class StartFermentationUseCase:

    def __init__(
        self,
        fermentation_repository: IFermentationRepository,
        sensor_repository:       ISensorRepository,
    ):
        self._fermentation_repo = fermentation_repository
        self._sensor_repo       = sensor_repository

    async def execute(self, session_id: int, circuit) -> FermentationSession:
        session = await self._fermentation_repo.get_session_by_id(session_id)
        if not session:
            raise FermentationSessionNotFoundException()

        if session.status == "running":
            raise FermentationAlreadyRunningException()

        if session.status != "scheduled":
            raise BadRequestException(
                f"No se puede iniciar una sesión en estado '{session.status}'"
            )

        now = datetime.now(timezone.utc)

        session = await self._fermentation_repo.update_session_status(
            session_id=session_id,
            status="running",
            actual_start=now,
        )

        active_sensors = circuit.get_active_sensors()
        for sensor_type in active_sensors:
            latest = await self._sensor_repo.get_latest_reading(
                circuit_id=circuit.id,
                sensor_type=sensor_type,
            )
            if latest:
                await self._fermentation_repo.update_sensor_initial(
                    session_id=session_id,
                    sensor_type=sensor_type,
                    value=latest.value,
                )

        thread_manager.start_session(
            circuit_id=circuit.id,
            session_id=session_id,
            active_sensors=active_sensors,
        )

        return session