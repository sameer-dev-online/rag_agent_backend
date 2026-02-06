"""
OpenAI embeddings using text-embedding-3-small.
"""

from typing import List
from dotenv import load_dotenv
import os

load_dotenv()  # reads .env into os.environ
from openai import AsyncOpenAI

from app.core.config import Settings
from app.core.errors import EmbeddingError
from app.models.document import DocumentChunk

from .base import BaseEmbedder


class OpenAIEmbedder(BaseEmbedder):
    """OpenAI embedding generator using text-embedding-3-small."""

    def __init__(self, settings: Settings):
        """
        Initialize OpenAI embedder.

        Args:
            settings (Settings): Application settings.
        """
        self.settings = settings
        self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = settings.openai_embedding_model
        self._dimensions = settings.openai_embedding_dimensions

    async def embed_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """
        Generate embeddings for document chunks using OpenAI API.

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

            # Call OpenAI API
            response = await self.client.embeddings.create(
                input=texts, model=self.model, dimensions=self._dimensions
            )

            # Assign embeddings to chunks
            for i, chunk in enumerate(chunks):
                chunk.embedding = response.data[i].embedding

            return chunks

        except Exception as e:
            raise EmbeddingError(
                f"Failed to generate embeddings using OpenAI: {str(e)}",
                details={"model": self.model, "chunk_count": len(chunks), "error": str(e)},
            )

    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query string using OpenAI API.

        Args:
            query (str): Query text.

        Returns:
            List[float]: Query embedding vector.

        Raises:
            EmbeddingError: If embedding generation fails.
        """
        try:
            response = await self.client.embeddings.create(
                input=[query], model=self.model, dimensions=self._dimensions
            )

            return response.data[0].embedding

        except Exception as e:
            raise EmbeddingError(
                f"Failed to generate query embedding using OpenAI: {str(e)}",
                details={"model": self.model, "error": str(e)},
            )

    @property
    def embedding_dimensions(self) -> int:
        """
        Get embedding vector dimensions.

        Returns:
            int: Number of dimensions (1536 for text-embedding-3-small).
        """
        return self._dimensions
