from modules.fermentation.infrastructure.adapters.MySQL import FermentationRepository
from core.database import AsyncSessionLocal


def get_fermentation_repository() -> FermentationRepository:
    return FermentationRepository(AsyncSessionLocal)