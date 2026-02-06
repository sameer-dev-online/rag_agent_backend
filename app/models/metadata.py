"""
Additional metadata models.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ProcessingMetadata(BaseModel):
    """Metadata about document processing."""

    processing_start_time: datetime = Field(
        default_factory=datetime.utcnow, description="Processing start time"
    )
    processing_end_time: Optional[datetime] = Field(None, description="Processing end time")
    processing_duration_ms: Optional[float] = Field(None, description="Processing duration in ms")
    chunks_created: int = Field(0, description="Number of chunks created")
    embeddings_generated: int = Field(0, description="Number of embeddings generated")
    errors: list = Field(default_factory=list, description="Processing errors")

    @property
    def duration_ms(self) -> Optional[float]:
        """
        Calculate processing duration in milliseconds.

        Returns:
            Optional[float]: Duration in milliseconds or None if not finished.
        """
        if self.processing_end_time:
            delta = self.processing_end_time - self.processing_start_time
            return delta.total_seconds() * 1000
        return None


class ChunkMetadata(BaseModel):
    """Extended metadata for a chunk."""

    source_page: Optional[int] = Field(None, description="Source page number")
    source_section: Optional[str] = Field(None, description="Source section name")
    language: Optional[str] = Field(None, description="Detected language")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata fields")
