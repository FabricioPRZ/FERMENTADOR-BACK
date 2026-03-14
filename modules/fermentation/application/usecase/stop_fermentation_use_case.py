from datetime import datetime, timezone
from modules.fermentation.domain.entities.entities import FermentationSession
from modules.fermentation.domain.repository import IFermentationRepository
from modules.sensors.domain.repository import ISensorRepository
from core.threads.sensor_thread_manager import thread_manager
from core.exceptions import (
    FermentationSessionNotFoundException,
    FermentationNotRunningException,
)


class StopFermentationUseCase:

    def __init__(
        self,
        fermentation_repository: IFermentationRepository,
        sensor_repository:       ISensorRepository,
    ):
        self._fermentation_repo = fermentation_repository
        self._sensor_repo       = sensor_repository

    async def execute(
        self,
        session_id:     int,
        circuit,
        interrupted_by: int | None = None,
    ) -> FermentationSession:
        session = await self._fermentation_repo.get_session_by_id(session_id)
        if not session:
            raise FermentationSessionNotFoundException()

        if session.status != "running":
            raise FermentationNotRunningException()

        now    = datetime.now(timezone.utc)
        status = "interrupted" if interrupted_by else "completed"

        active_sensors = thread_manager.get_active_sensors(circuit.id)
        for sensor_type in active_sensors:
            latest = await self._sensor_repo.get_latest_reading(
                circuit_id=circuit.id,
                sensor_type=sensor_type,
            )
            if latest:
                await self._fermentation_repo.update_sensor_final(
                    session_id=session_id,
                    sensor_type=sensor_type,
                    value=latest.value,
                )

        await self._calculate_efficiency(session_id)

        session = await self._fermentation_repo.update_session_status(
            session_id=session_id,
            status=status,
            actual_end=now,
            interrupted_by=interrupted_by,
        )

        report = await self._fermentation_repo.get_report_by_session(session_id)
        if report:
            await self._fermentation_repo.create_report_history(
                report_id=report.id,
                user_id=session.user_id,
                action="generated",
            )

        thread_manager.stop_session(circuit.id)
        return session

    async def _calculate_efficiency(self, session_id: int) -> None:
        report = await self._fermentation_repo.get_report_by_session(session_id)
        if not report:
            return

        factor              = await self._fermentation_repo.get_active_formula_factor()
        ethanol_detected    = report.alcohol_final or report.alcohol_last_reading
        theoretical_ethanol = report.initial_sugar * factor
        efficiency          = None

        if ethanol_detected and theoretical_ethanol > 0:
            efficiency = min(
                100.0,
                round((ethanol_detected / theoretical_ethanol) * 100, 2)
            )

        report.ethanol_detected    = ethanol_detected
        report.theoretical_ethanol = theoretical_ethanol
        report.efficiency          = efficiency
        await self._fermentation_repo.update_report(report)