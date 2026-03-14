from modules.circuits.application.usecase.create_circuit_use_case import CreateCircuitUseCase
from modules.circuits.application.usecase.activate_circuit_use_case import ActivateCircuitUseCase
from modules.circuits.application.usecase.get_circuit_status_use_case import GetCircuitStatusUseCase
from modules.circuits.infrastructure.adapters.MySQL import CircuitRepository
from modules.circuits.domain.dto.schemas import (
    CircuitResponse,
    CreateCircuitResponse,
)
from core.database import AsyncSessionLocal
from core.exceptions import CircuitNotFoundException


def _repo():
    return CircuitRepository(AsyncSessionLocal)


def _to_response(circuit) -> CircuitResponse:
    return CircuitResponse(
        id=circuit.id,
        activation_code=circuit.activation_code,
        is_active=circuit.is_active,
        motor_on=circuit.motor_on,
        pump_on=circuit.pump_on,
        sensor_alcohol_on=circuit.sensor_alcohol_on,
        sensor_density_on=circuit.sensor_density_on,
        sensor_conductivity_on=circuit.sensor_conductivity_on,
        sensor_ph_on=circuit.sensor_ph_on,
        sensor_temperature_on=circuit.sensor_temperature_on,
        sensor_turbidity_on=circuit.sensor_turbidity_on,
        sensor_rpm_on=circuit.sensor_rpm_on,
        activated_at=circuit.activated_at,
        created_at=circuit.created_at,
        active_sensors=circuit.get_active_sensors(),
    )


async def create() -> CreateCircuitResponse:
    circuit = await CreateCircuitUseCase(_repo()).execute()
    return CreateCircuitResponse(
        id=circuit.id,
        activation_code=circuit.activation_code,
        created_at=circuit.created_at,
    )


async def get_my_circuit(circuit_id: int) -> CircuitResponse:
    """
    Recibe el circuit_id que viene del usuario autenticado (users.circuit_id).
    """
    if not circuit_id:
        raise CircuitNotFoundException()
    circuit = await GetCircuitStatusUseCase(_repo()).get_by_id(circuit_id)
    return _to_response(circuit)


async def get_by_id(circuit_id: int) -> CircuitResponse:
    circuit = await GetCircuitStatusUseCase(_repo()).get_by_id(circuit_id)
    return _to_response(circuit)