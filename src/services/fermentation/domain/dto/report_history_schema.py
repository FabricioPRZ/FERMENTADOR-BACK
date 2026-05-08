from pydantic import BaseModel
from datetime import datetime


class ReportHistoryResponse(BaseModel):
    id:          int
    report_id:   int
    user_id:     int
    action:      str
    occurred_at: datetime | None
