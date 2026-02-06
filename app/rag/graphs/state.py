"""
LangGraph state definition for document ingestion workflow.
"""

from typing import List, Optional, TypedDict

from app.models.document import Document, DocumentChunk


class IngestionState(TypedDict):
    """State for document ingestion workflow."""

    # Input
    file_path: str

    # Processing stages
    document: Optional[Document]
    chunks: Optional[List[DocumentChunk]]
    embedded_chunks: Optional[List[DocumentChunk]]

    # Timing
    processing_start_time: float
    processing_end_time: Optional[float]

    # Status and errors
    errors: List[str]
    status: str  # pending, in_progress, completed, failed
