"""
API router registration.
"""

from fastapi import APIRouter

from app.core.config import get_settings
from app.models.schemas import HealthResponse

from .upload import router as upload_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(upload_router, tags=["upload"])


# Health check endpoint
@api_router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse: Health status and version info.
    """
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
    )
