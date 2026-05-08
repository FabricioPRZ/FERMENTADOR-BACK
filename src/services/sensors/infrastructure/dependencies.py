from src.services.sensors.infrastructure.adapters.MySQL import SensorRepository
from src.core.database import AsyncSessionLocal


def get_sensor_repository() -> SensorRepository:
    return SensorRepository(AsyncSessionLocal)