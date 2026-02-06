"""
API request and response schemas.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class FileProcessingDetail(BaseModel):
    """Details about a single file's processing result."""

    filename: str = Field(..., description="Name of the processed file")
    file_size_bytes: int = Field(..., description="File size in bytes")
    chunks_created: int = Field(..., description="Number of chunks created from this file")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    status: str = Field(..., description="Processing status (success/failed)")
    error: Optional[str] = Field(None, description="Error message if processing failed")


class UploadResponse(BaseModel):
    """Response schema for file upload endpoint."""

    success: bool = Field(..., description="Whether the upload was successful")
    files_processed: int = Field(..., description="Number of files successfully processed")
    chunks_created: int = Field(..., description="Total number of chunks created")
    message: str = Field(..., description="Summary message")
    details: List[FileProcessingDetail] = Field(..., description="Per-file processing details")


class ErrorResponse(BaseModel):
    """Response schema for errors."""

    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
