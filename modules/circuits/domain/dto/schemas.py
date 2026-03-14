from pydantic import BaseModel
from datetime import datetime


class CreateCircuitResponse(BaseModel):
    id:              int
    activation_code: str
    created_at:      datetime | None


class ActivateCircuitRequest(BaseModel):
    activation_code: str


class WSCommandRequest(BaseModel):
    command:    str
    parameters: dict = {}


class CircuitResponse(BaseModel):
    id:                     int
    activation_code:        str
    is_active:              bool
    motor_on:               bool
    pump_on:                bool
    sensor_alcohol_on:      bool
    sensor_density_on:      bool
    sensor_conductivity_on: bool
    sensor_ph_on:           bool
    sensor_temperature_on:  bool
    sensor_turbidity_on:    bool
    sensor_rpm_on:          bool
    activated_at:           datetime | None
    created_at:             datetime | None
    active_sensors:         list[str]