from pydantic import BaseModel
from datetime import datetime


class UpdateFormulaRequest(BaseModel):
    name:              str | None = None
    conversion_factor: float | None = None
    description:       str | None = None


class FormulaResponse(BaseModel):
    id:                int
    name:              str
    conversion_factor: float
    description:       str | None
    is_active:         bool
    updated_by:        int | None
    updated_at:        datetime | None
    created_at:        datetime | None