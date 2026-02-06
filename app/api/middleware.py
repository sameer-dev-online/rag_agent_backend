"""
FastAPI middleware for error handling and logging.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.errors import RAGException
from app.core.logging import get_logger
from app.models.schemas import ErrorResponse

logger = get_logger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to handle exceptions and convert to JSON responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Handle request and catch exceptions.

        Args:
            request (Request): FastAPI request.
            call_next (Callable): Next middleware/handler.

        Returns:
            Response: HTTP response.
        """
        try:
            response = await call_next(request)
            return response

        except RAGException as e:
            # Handle custom RAG exceptions
            error_response = ErrorResponse(
                success=False,
                error=e.message,
                details=e.details,
            )

            logger.error(
                f"RAG error: {e.message}",
                extra={
                    "error_type": type(e).__name__,
                    "status_code": e.status_code,
                    "details": e.details,
                },
            )

            return Response(
                content=error_response.model_dump_json(),
                status_code=e.status_code,
                media_type="application/json",
            )

        except Exception as e:
            # Handle unexpected exceptions
            error_response = ErrorResponse(
                success=False,
                error="Internal server error",
                details={"error": str(e)},
            )

            logger.exception("Unexpected error occurred")

            return Response(
                content=error_response.model_dump_json(),
                status_code=500,
                media_type="application/json",
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log requests with timing information."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request and response.

        Args:
            request (Request): FastAPI request.
            call_next (Callable): Next middleware/handler.

        Returns:
            Response: HTTP response.
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={"request_id": request_id},
        )

        # Time request
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "duration_ms": duration_ms,
                "status_code": response.status_code,
            },
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
