"""
Base text splitter interface.
"""

from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.models.document import Document, DocumentChunk


class BaseTextSplitter(ABC):
    """Abstract base class for text splitters."""

    @abstractmethod
    async def split(self, document: Document) -> List[DocumentChunk]:
        """
        Split document into chunks.

        Args:
            document (Document): Document to split.

        Returns:
            List[DocumentChunk]: List of document chunks.
        """
        pass

    def _create_chunks(
        self, document: Document, text_chunks: List[str]
    ) -> List[DocumentChunk]:
        """
        Create DocumentChunk objects from text chunks.

        Args:
            document (Document): Source document.
            text_chunks (List[str]): List of text chunks.

        Returns:
            List[DocumentChunk]: List of document chunks with metadata.
        """
        chunks = []
        for idx, text in enumerate(text_chunks):
            if text.strip():  # Only create chunks with content
                chunk = DocumentChunk(
                    document_id=document.id,
                    content=text.strip(),
                    chunk_index=idx,
                    metadata=document.metadata,
                )
                chunks.append(chunk)
        return chunks
