"""
In-memory vector store for testing.
"""

import numpy as np
from typing import Dict, List, Optional
from uuid import UUID

from app.core.errors import VectorStoreError
from app.models.document import DocumentChunk

from .base import BaseVectorStore


class MemoryVectorStore(BaseVectorStore):
    """In-memory vector store for testing purposes."""

    def __init__(self):
        """Initialize in-memory vector store."""
        self.chunks: Dict[str, DocumentChunk] = {}

    async def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        """
        Add document chunks to memory.

        Args:
            chunks (List[DocumentChunk]): Chunks with embeddings to store.

        Raises:
            VectorStoreError: If storing chunks fails.
        """
        if not chunks:
            return

        try:
            for chunk in chunks:
                self.chunks[str(chunk.id)] = chunk

        except Exception as e:
            raise VectorStoreError(
                f"Failed to add chunks to memory store: {str(e)}",
                details={"chunk_count": len(chunks), "error": str(e)},
            )

    async def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 5,
        filter_metadata: Optional[Dict] = None,
    ) -> List[DocumentChunk]:
        """
        Search for similar chunks using cosine similarity.

        Args:
            query_embedding (List[float]): Query embedding vector.
            k (int): Number of results to return.
            filter_metadata (Optional[Dict]): Metadata filters.

        Returns:
            List[DocumentChunk]: Most similar chunks.

        Raises:
            VectorStoreError: If search fails.
        """
        try:
            if not self.chunks:
                return []

            # Filter chunks based on metadata
            filtered_chunks = list(self.chunks.values())
            if filter_metadata:
                filtered_chunks = [
                    chunk
                    for chunk in filtered_chunks
                    if self._matches_filter(chunk, filter_metadata)
                ]

            if not filtered_chunks:
                return []

            # Calculate cosine similarity for each chunk
            query_vec = np.array(query_embedding)
            similarities = []

            for chunk in filtered_chunks:
                if chunk.embedding:
                    chunk_vec = np.array(chunk.embedding)
                    # Cosine similarity
                    similarity = np.dot(query_vec, chunk_vec) / (
                        np.linalg.norm(query_vec) * np.linalg.norm(chunk_vec)
                    )
                    similarities.append((chunk, similarity))

            # Sort by similarity (descending) and return top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_chunks = [chunk for chunk, _ in similarities[:k]]

            return top_chunks

        except Exception as e:
            raise VectorStoreError(
                f"Failed to search memory store: {str(e)}",
                details={"k": k, "error": str(e)},
            )

    async def delete_by_document_id(self, document_id: str) -> None:
        """
        Delete all chunks for a specific document.

        Args:
            document_id (str): Document ID to delete.

        Raises:
            VectorStoreError: If deletion fails.
        """
        try:
            chunk_ids_to_delete = [
                chunk_id
                for chunk_id, chunk in self.chunks.items()
                if str(chunk.document_id) == document_id
            ]

            for chunk_id in chunk_ids_to_delete:
                del self.chunks[chunk_id]

        except Exception as e:
            raise VectorStoreError(
                f"Failed to delete document from memory store: {str(e)}",
                details={"document_id": document_id, "error": str(e)},
            )

    async def count(self) -> int:
        """
        Get total number of chunks in the store.

        Returns:
            int: Number of chunks.
        """
        return len(self.chunks)

    def _matches_filter(self, chunk: DocumentChunk, filter_metadata: Dict) -> bool:
        """
        Check if chunk matches metadata filters.

        Args:
            chunk (DocumentChunk): Chunk to check.
            filter_metadata (Dict): Metadata filters.

        Returns:
            bool: True if chunk matches all filters.
        """
        for key, value in filter_metadata.items():
            if key == "document_id":
                if str(chunk.document_id) != value:
                    return False
            elif hasattr(chunk.metadata, key):
                if getattr(chunk.metadata, key) != value:
                    return False
        return True
