from pydantic import BaseModel
from datetime import datetime


class ScheduleFermentationRequest(BaseModel):
    circuit_id:      int
    scheduled_start: datetime
    scheduled_end:   datetime
    initial_sugar:   float


class StopFermentationRequest(BaseModel):
    interrupted: bool = False


class FermentationSessionResponse(BaseModel):
    id:              int
    circuit_id:      int
    user_id:         int
    formula_id:      int
    scheduled_start: datetime
    scheduled_end:   datetime
    actual_start:    datetime | None
    actual_end:      datetime | None
    status:          str
    interrupted_by:  int | None
    created_at:      datetime | None


class FermentationReportResponse(BaseModel):
    id:                          int
    session_id:                  int
    initial_sugar:               float
    final_sugar:                 float | None
    ethanol_detected:            float | None
    theoretical_ethanol:         float | None
    efficiency:                  float | None
    alcohol_initial:             float | None
    alcohol_final:               float | None
    alcohol_deactivated_at:      datetime | None
    alcohol_last_reading:        float | None
    density_initial:             float | None
    density_final:               float | None
    density_deactivated_at:      datetime | None
    density_last_reading:        float | None
    conductivity_initial:        float | None
    conductivity_final:          float | None
    conductivity_deactivated_at: datetime | None
    conductivity_last_reading:   float | None
    ph_initial:                  float | None
    ph_final:                    float | None
    ph_deactivated_at:           datetime | None
    ph_last_reading:             float | None
    temperature_initial:         float | None
    temperature_final:           float | None
    temperature_deactivated_at:  datetime | None
    temperature_last_reading:    float | None
    turbidity_initial:           float | None
    turbidity_final:             float | None
    turbidity_deactivated_at:    datetime | None
    turbidity_last_reading:      float | None
    rpm_initial:                 float | None
    rpm_final:                   float | None
    rpm_deactivated_at:          datetime | None
    rpm_last_reading:            float | None
    notes:                       str | None
    generated_at:                datetime | None


class ReportHistoryResponse(BaseModel):
    id:          int
    report_id:   int
    user_id:     int
    action:      str
    occurred_at: datetime | None