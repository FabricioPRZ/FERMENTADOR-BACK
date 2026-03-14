from modules.notifications.infrastructure.adapters.MySQL import NotificationRepository
from core.database import AsyncSessionLocal


def get_notification_repository() -> NotificationRepository:
    return NotificationRepository(AsyncSessionLocal)