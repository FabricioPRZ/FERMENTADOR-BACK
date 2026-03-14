from modules.sensors.infrastructure.adapters.MySQL import SensorRepository
from core.database import AsyncSessionLocal


def get_sensor_repository() -> SensorRepository:
    return SensorRepository(AsyncSessionLocal)