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


class RetrievedChunk(BaseModel):
    """Schema for a retrieved document chunk."""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Parent document identifier")
    content: str = Field(..., description="Chunk text content")
    chunk_index: int = Field(..., description="Index of chunk in document")
    filename: str = Field(..., description="Source filename")
    source_type: str = Field(..., description="Source file type (pdf, txt, docx)")
    similarity_score: Optional[float] = Field(None, description="Similarity score from vector search")


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    query: str = Field(..., min_length=1, max_length=2000, description="User query text")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of chunks to retrieve")
    filter_metadata: Optional[dict] = Field(None, description="Metadata filters for retrieval")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    success: bool = Field(..., description="Whether the query was successful")
    answer: str = Field(..., description="Generated answer based on retrieved context")
    sources: List[str] = Field(..., description="List of source filenames used")
    retrieved_chunks: List[RetrievedChunk] = Field(..., description="Retrieved document chunks")
    query_time_ms: float = Field(..., description="Query processing time in milliseconds")
    session_id: Optional[str] = Field(None, description="Session ID if provided")
    error: Optional[str] = Field(None, description="Error message if query failed")
