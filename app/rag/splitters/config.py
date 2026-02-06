"""
Text splitter configuration.
"""

from typing import List

from pydantic import BaseModel, Field

from app.core.constants import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE


class SplitterConfig(BaseModel):
    """Configuration for text splitting."""

    chunk_size: int = Field(
        default=DEFAULT_CHUNK_SIZE,
        description="Maximum size of each chunk in characters",
        gt=0,
    )

    chunk_overlap: int = Field(
        default=DEFAULT_CHUNK_OVERLAP,
        description="Number of characters to overlap between chunks",
        ge=0,
    )

    separators: List[str] = Field(
        default=["\n\n", "\n", ". ", " ", ""],
        description="List of separators to use for splitting, in order of preference",
    )

    keep_separator: bool = Field(
        default=True, description="Whether to keep separators in the chunks"
    )

    def validate_config(self) -> None:
        """
        Validate that chunk overlap is less than chunk size.

        Raises:
            ValueError: If overlap >= chunk_size.
        """
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                f"chunk_overlap ({self.chunk_overlap}) must be less than chunk_size ({self.chunk_size})"
            )
