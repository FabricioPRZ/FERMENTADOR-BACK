from pydantic import BaseModel
from datetime import datetime


class CreateCircuitResponse(BaseModel):
    id:              int
    activation_code: str
    created_at:      datetime | None
