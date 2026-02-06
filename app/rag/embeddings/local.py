"""
Local embeddings using sentence-transformers.
"""

from typing import List

from sentence_transformers import SentenceTransformer

from app.core.config import Settings
from app.core.errors import EmbeddingError
from app.models.document import DocumentChunk

from .base import BaseEmbedder


class LocalEmbedder(BaseEmbedder):
    """Local embedding generator using sentence-transformers."""

    def __init__(self, settings: Settings):
        """
        Initialize local embedder.

        Args:
            settings (Settings): Application settings.
        """
        self.settings = settings
        self.model_name = settings.local_embedding_model

        try:
            # Load sentence-transformers model
            self.model = SentenceTransformer(self.model_name)
            self._dimensions = self.model.get_sentence_embedding_dimension()
        except Exception as e:
            raise EmbeddingError(
                f"Failed to load local embedding model: {self.model_name}",
                details={"model": self.model_name, "error": str(e)},
            )

    async def embed_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """
        Generate embeddings for document chunks using local model.

        Args:
            chunks (List[DocumentChunk]): List of chunks to embed.

        Returns:
            List[DocumentChunk]: Chunks with embeddings populated.

        Raises:
            EmbeddingError: If embedding generation fails.
        """
        if not chunks:
            return chunks

        try:
            # Extract text from chunks
            texts = [chunk.content for chunk in chunks]

            # Generate embeddings
            embeddings = self.model.encode(texts, convert_to_numpy=True)

            # Assign embeddings to chunks
            for i, chunk in enumerate(chunks):
                chunk.embedding = embeddings[i].tolist()

            return chunks

        except Exception as e:
            raise EmbeddingError(
                f"Failed to generate embeddings using local model: {str(e)}",
                details={
                    "model": self.model_name,
                    "chunk_count": len(chunks),
                    "error": str(e),
                },
            )

    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query string using local model.

        Args:
            query (str): Query text.

        Returns:
            List[float]: Query embedding vector.

        Raises:
            EmbeddingError: If embedding generation fails.
        """
        try:
            embedding = self.model.encode([query], convert_to_numpy=True)
            return embedding[0].tolist()

        except Exception as e:
            raise EmbeddingError(
                f"Failed to generate query embedding using local model: {str(e)}",
                details={"model": self.model_name, "error": str(e)},
            )

    @property
    def embedding_dimensions(self) -> int:
        """
        Get embedding vector dimensions.

        Returns:
            int: Number of dimensions in embedding vectors.
        """
        return self._dimensions
