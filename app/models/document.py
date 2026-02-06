"""
Document-related Pydantic models.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata for a document."""

    filename: str = Field(..., description="Original filename")
    file_size_bytes: int = Field(..., description="File size in bytes")
    file_hash: str = Field(..., description="SHA-256 hash of file content")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    source_type: str = Field(..., description="File type (pdf, txt, docx)")
    page_count: Optional[int] = Field(None, description="Number of pages (for PDFs)")
    custom_metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")


class Document(BaseModel):
    """A document with content and metadata."""

    id: UUID = Field(default_factory=uuid4, description="Unique document ID")
    content: str = Field(..., description="Document text content")
    metadata: DocumentMetadata = Field(..., description="Document metadata")

    def __len__(self) -> int:
        """
        Get document content length.

        Returns:
            int: Length of document content.
        """
        return len(self.content)


class DocumentChunk(BaseModel):
    """A chunk of a document with optional embedding."""

    id: UUID = Field(default_factory=uuid4, description="Unique chunk ID")
    document_id: UUID = Field(..., description="Parent document ID")
    content: str = Field(..., description="Chunk text content")
    chunk_index: int = Field(..., description="Index of chunk in document")
    metadata: DocumentMetadata = Field(..., description="Parent document metadata")
    embedding: Optional[List[float]] = Field(None, description="Embedding vector")

    def __len__(self) -> int:
        """
        Get chunk content length.

        Returns:
            int: Length of chunk content.
        """
        return len(self.content)
