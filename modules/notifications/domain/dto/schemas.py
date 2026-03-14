from pydantic import BaseModel
from datetime import datetime


class NotificationResponse(BaseModel):
    id:         int
    user_id:    int
    message:    str
    type:       str
    status:     str
    session_id: int | None
    created_at: datetime | None