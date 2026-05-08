from pydantic import BaseModel
from datetime import datetime


class ScheduleFermentationRequest(BaseModel):
    circuit_id:      int
    scheduled_start: datetime
    scheduled_end:   datetime
    initial_sugar:   float
