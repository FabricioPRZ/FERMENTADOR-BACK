from modules.notifications.application.usecase.mark_read_use_case import MarkReadUseCase
from modules.notifications.infrastructure.adapters.MySQL import NotificationRepository
from modules.notifications.domain.dto.schemas import NotificationResponse
from core.database import AsyncSessionLocal


def _repo():
    return NotificationRepository(AsyncSessionLocal)


def _to_response(n) -> NotificationResponse:
    return NotificationResponse(
        id=n.id,
        user_id=n.user_id,
        message=n.message,
        type=n.type,
        status=n.status,
        session_id=n.session_id,
        created_at=n.created_at,
    )


async def get_all(user_id: int, only_unread: bool) -> list[NotificationResponse]:
    notifications = await _repo().get_by_user(
        user_id=user_id,
        only_unread=only_unread,
    )
    return [_to_response(n) for n in notifications]


async def mark_one_as_read(notification_id: int) -> NotificationResponse | None:
    notification = await MarkReadUseCase(_repo()).execute_one(notification_id)
    return _to_response(notification) if notification else None


async def mark_all_as_read(user_id: int) -> None:
    await MarkReadUseCase(_repo()).execute_all(user_id)