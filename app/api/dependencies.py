"""
Dependency injection for FastAPI.
"""

from functools import lru_cache

from app.agents.ingestion.agent import IngestionAgent
from app.agents.query.agent import QueryAgent
from app.core.config import Settings, get_settings
from app.services.query_service import QueryService
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


@lru_cache()
def get_query_service() -> QueryService:
    """
    Get cached query service instance.

    Returns:
        QueryService: Query service with dependencies.
    """
    settings = get_settings()
    return QueryService(settings)


@lru_cache()
def get_query_agent() -> QueryAgent:
    """
    Get cached query agent instance.

    Returns:
        QueryAgent: Query agent.
    """
    settings = get_settings()
    return QueryAgent(settings)
