"""
Vector store factory.
"""

from app.core.config import Settings
from app.core.constants import VectorStoreType

from .base import BaseVectorStore
from .chroma import ChromaLocalVectorStore
from .chroma_cloud import ChromaCloudVectorStore
from .memory import MemoryVectorStore


class VectorStoreFactory:
    """Factory for creating vector stores based on configuration."""

    @classmethod
    def create_vector_store(cls, settings: Settings) -> BaseVectorStore:
        """
        Create appropriate vector store based on settings.

        Args:
            settings (Settings): Application settings.

        Returns:
            BaseVectorStore: Vector store instance.

        Raises:
            ValueError: If vector store type is not supported.
        """
        if settings.vector_store == VectorStoreType.CHROMA_LOCAL:
            return ChromaLocalVectorStore(settings)
        elif settings.vector_store == VectorStoreType.CHROMA_CLOUD:
            return ChromaCloudVectorStore(settings)
        elif settings.vector_store == VectorStoreType.MEMORY:
            return MemoryVectorStore()
        else:
            raise ValueError(f"Unsupported vector store type: {settings.vector_store}")
