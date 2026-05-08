from src.services.fermentation.infrastructure.adapters.MySQL import FermentationRepository
from src.core.database import AsyncSessionLocal


def get_fermentation_repository() -> FermentationRepository:
    return FermentationRepository(AsyncSessionLocal)