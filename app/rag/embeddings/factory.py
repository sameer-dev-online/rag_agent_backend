"""
Embedder factory.
"""

from app.core.config import Settings
from app.core.constants import EmbeddingProvider

from .base import BaseEmbedder
from .local import LocalEmbedder
from .openai import OpenAIEmbedder


class EmbedderFactory:
    """Factory for creating embedders based on configuration."""

    @classmethod
    def create_embedder(cls, settings: Settings) -> BaseEmbedder:
        """
        Create appropriate embedder based on settings.

        Args:
            settings (Settings): Application settings.

        Returns:
            BaseEmbedder: Embedder instance.

        Raises:
            ValueError: If embedding provider is not supported.
        """
        if settings.embedding_provider == EmbeddingProvider.OPENAI:
            return OpenAIEmbedder(settings)
        elif settings.embedding_provider == EmbeddingProvider.LOCAL:
            return LocalEmbedder(settings)
        else:
            raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")
