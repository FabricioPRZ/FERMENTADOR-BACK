import uuid
from modules.circuits.domain.entities.entities import Circuit
from modules.circuits.domain.repository import ICircuitRepository


class CreateCircuitUseCase:

    def __init__(self, repository: ICircuitRepository):
        self._repo = repository

    async def execute(self) -> Circuit:
        # Genera un código de activación único de 8 caracteres en mayúsculas
        activation_code = uuid.uuid4().hex[:8].upper()
        return await self._repo.create(activation_code)