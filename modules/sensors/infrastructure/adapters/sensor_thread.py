import asyncio
import logging
from core.threads.base_sensor_thread import BaseSensorThread
from core.rabbitmq.connection import rabbitmq
from core.websocket.schemas import ESP32SensorPayload

logger = logging.getLogger(__name__)


class SensorThread(BaseSensorThread):
    """
    Hilo dedicado por sensor activo en una sesión.
    Se suscribe a su queue exclusiva en RabbitMQ y procesa lecturas.
    """

    def __init__(
        self,
        circuit_id:  int,
        session_id:  int,
        sensor_type: str,
    ):
        super().__init__(circuit_id, session_id, sensor_type)
        self._queue_name = f"sensor.{sensor_type}.{circuit_id}"

    async def process_reading(self, payload: ESP32SensorPayload) -> None:
        from modules.sensors.application.usecase.get_history_use_case import SaveReadingUseCase
        from modules.sensors.infrastructure.adapters.MySQL import SensorRepository
        from core.database import AsyncSessionLocal

        repo = SensorRepository(AsyncSessionLocal)
        uc   = SaveReadingUseCase(repo)

        if payload.active:
            await uc.execute(
                circuit_id=payload.circuit_id,
                sensor_type=payload.sensor_type,
                value=payload.value,
                session_id=self._session_id,
            )
        else:
            await uc.execute_deactivation(
                circuit_id=payload.circuit_id,
                sensor_type=payload.sensor_type,
                session_id=self._session_id,
                value=payload.value,
            )
            self.stop()

    async def _run_async(self) -> None:
        channel = await rabbitmq.get_channel()
        queue   = await channel.declare_queue(self._queue_name, durable=True)

        logger.info(
            f"[SensorThread] Escuchando → {self._queue_name}"
        )

        async with queue.iterator() as messages:
            async for message in messages:
                if self._stop_event.is_set():
                    break
                async with message.process():
                    import json
                    data    = json.loads(message.body.decode())
                    payload = ESP32SensorPayload(**data)
                    await self.process_reading(payload)