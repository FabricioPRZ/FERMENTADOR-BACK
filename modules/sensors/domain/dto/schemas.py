from pydantic import BaseModel
from datetime import datetime


class SensorReadingResponse(BaseModel):
    id:          int
    circuit_id:  int
    sensor_type: str
    value:       float
    session_id:  int | None
    timestamp:   datetime | None


class SensorHistoryResponse(BaseModel):
    circuit_id:  int
    sensor_type: str
    readings:    list[SensorReadingResponse]