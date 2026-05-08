from src.services.notifications.infrastructure.adapters.MySQL import NotificationRepository
from src.core.database import AsyncSessionLocal


def get_notification_repository() -> NotificationRepository:
    return NotificationRepository(AsyncSessionLocal)