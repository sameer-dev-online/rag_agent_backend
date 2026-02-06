"""
Base vector store interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from app.models.document import DocumentChunk


class BaseVectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    async def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        """
        Add document chunks to the vector store.

        Args:
            chunks (List[DocumentChunk]): Chunks with embeddings to store.

        Raises:
            VectorStoreError: If storing chunks fails.
        """
        pass

    @abstractmethod
    async def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 5,
        filter_metadata: Optional[Dict] = None,
    ) -> List[DocumentChunk]:
        """
        Search for similar chunks using embedding similarity.

        Args:
            query_embedding (List[float]): Query embedding vector.
            k (int): Number of results to return.
            filter_metadata (Optional[Dict]): Metadata filters.

        Returns:
            List[DocumentChunk]: Most similar chunks.

        Raises:
            VectorStoreError: If search fails.
        """
        pass

    @abstractmethod
    async def delete_by_document_id(self, document_id: str) -> None:
        """
        Delete all chunks for a specific document.

        Args:
            document_id (str): Document ID to delete.

        Raises:
            VectorStoreError: If deletion fails.
        """
        pass

    @abstractmethod
    async def count(self) -> int:
        """
        Get total number of chunks in the store.

        Returns:
            int: Number of chunks.
        """
        pass
