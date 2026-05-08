from src.services.notifications.application.usecase.mark_read_use_case import MarkReadUseCase
from src.services.notifications.infrastructure.adapters.MySQL import NotificationRepository
from src.services.notifications.domain.dto.notification_schema import NotificationResponse
from src.core.database import AsyncSessionLocal


async def mark_one_as_read(notification_id: int) -> NotificationResponse | None:
    repo = NotificationRepository(AsyncSessionLocal)
    notification = await MarkReadUseCase(repo).execute_one(notification_id)
    return NotificationResponse.from_entity(notification) if notification else None
