"""
Dependency injection for FastAPI.
"""

from functools import lru_cache

from app.agents.ingestion.agent import IngestionAgent
from app.core.config import Settings, get_settings
from app.services.upload_service import UploadService


@lru_cache()
def get_upload_service() -> UploadService:
    """
    Get cached upload service instance.

    Returns:
        UploadService: Upload service with dependencies.
    """
    settings = get_settings()
    return UploadService(settings)


@lru_cache()
def get_ingestion_agent() -> IngestionAgent:
    """
    Get cached ingestion agent instance.

    Returns:
        IngestionAgent: Ingestion agent.
    """
    settings = get_settings()
    return IngestionAgent(settings)
