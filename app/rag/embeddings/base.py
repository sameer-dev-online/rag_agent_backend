"""
Base embedder interface.
"""

from abc import ABC, abstractmethod
from typing import List

from app.models.document import DocumentChunk


class BaseEmbedder(ABC):
    """Abstract base class for embedding generation."""

    @abstractmethod
    async def embed_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """
        Generate embeddings for document chunks.

        Args:
            chunks (List[DocumentChunk]): List of chunks to embed.

        Returns:
            List[DocumentChunk]: Chunks with embeddings populated.

        Raises:
            EmbeddingError: If embedding generation fails.
        """
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query string.

        Args:
            query (str): Query text.

        Returns:
            List[float]: Query embedding vector.

        Raises:
            EmbeddingError: If embedding generation fails.
        """
        pass

    @property
    @abstractmethod
    def embedding_dimensions(self) -> int:
        """
        Get embedding vector dimensions.

        Returns:
            int: Number of dimensions in embedding vectors.
        """
        pass
