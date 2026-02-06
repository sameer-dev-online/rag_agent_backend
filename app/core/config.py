"""
Configuration management using Pydantic Settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHROMA_CLOUD_HOST,
    DEFAULT_CHROMA_CLOUD_PORT,
    DEFAULT_CHROMA_COLLECTION_NAME,
    DEFAULT_LOCAL_EMBEDDING_MODEL,
    DEFAULT_MAX_FILE_SIZE_MB,
    DEFAULT_MAX_FILES_PER_REQUEST,
    DEFAULT_OPENAI_EMBEDDING_DIMENSIONS,
    DEFAULT_OPENAI_EMBEDDING_MODEL,
    EmbeddingProvider,
    VectorStoreType,
)
from .errors import ConfigurationError


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # App settings
    app_name: str = "RAG Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # API settings
    api_v1_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000

    # File upload settings
    max_file_size_mb: float = DEFAULT_MAX_FILE_SIZE_MB
    max_files_per_request: int = DEFAULT_MAX_FILES_PER_REQUEST
    upload_dir: Path = Path("data/uploads")

    # Chunking settings
    chunk_size: int = DEFAULT_CHUNK_SIZE
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP

    # Embedding settings
    embedding_provider: EmbeddingProvider = EmbeddingProvider.OPENAI
    openai_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_embedding_model: str = DEFAULT_OPENAI_EMBEDDING_MODEL
    openai_embedding_dimensions: int = DEFAULT_OPENAI_EMBEDDING_DIMENSIONS
    local_embedding_model: str = DEFAULT_LOCAL_EMBEDDING_MODEL

    # Vector store settings
    vector_store: VectorStoreType = VectorStoreType.CHROMA_LOCAL

    # Chroma Local settings
    chroma_persist_dir: Path = Path("data/vector_store")
    chroma_collection_name: str = DEFAULT_CHROMA_COLLECTION_NAME

    # Chroma Cloud settings
    chroma_cloud_api_key: Optional[str] = Field(default=None, validation_alias="CHROMA_CLOUD_API_KEY")
    chroma_cloud_host: str = DEFAULT_CHROMA_CLOUD_HOST
    chroma_cloud_port: int = DEFAULT_CHROMA_CLOUD_PORT
    chroma_cloud_tenant: Optional[str] = Field(default=None, validation_alias="CHROMA_CLOUD_TENANT")
    chroma_cloud_database: Optional[str] = Field(default=None, validation_alias="CHROMA_CLOUD_DATABASE")

    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, v: int, info) -> int:
        """
        Validate that chunk overlap is less than chunk size.

        Args:
            v (int): Chunk overlap value.
            info: Validation info containing other fields.

        Returns:
            int: Validated chunk overlap.

        Raises:
            ValueError: If overlap >= chunk_size.
        """
        chunk_size = info.data.get("chunk_size", DEFAULT_CHUNK_SIZE)
        if v >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        return v

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v: Optional[str], info) -> Optional[str]:
        """
        Validate OpenAI API key is provided when using OpenAI embeddings.

        Args:
            v (Optional[str]): OpenAI API key.
            info: Validation info containing other fields.

        Returns:
            Optional[str]: Validated API key.

        Raises:
            ConfigurationError: If key is missing when OpenAI provider is selected.
        """
        provider = info.data.get("embedding_provider", EmbeddingProvider.OPENAI)
        if provider == EmbeddingProvider.OPENAI and not v:
            raise ConfigurationError(
                "OPENAI_API_KEY environment variable is required when using OpenAI embeddings"
            )
        return v

    @field_validator("chroma_cloud_api_key")
    @classmethod
    def validate_chroma_cloud_key(cls, v: Optional[str], info) -> Optional[str]:
        """
        Validate Chroma Cloud API key is provided when using Chroma Cloud.

        Args:
            v (Optional[str]): Chroma Cloud API key.
            info: Validation info containing other fields.

        Returns:
            Optional[str]: Validated API key.

        Raises:
            ConfigurationError: If key is missing when Chroma Cloud is selected.
        """
        provider = info.data.get("vector_store", VectorStoreType.CHROMA_LOCAL)
        if provider == VectorStoreType.CHROMA_CLOUD and not v:
            raise ConfigurationError(
                "CHROMA_CLOUD_API_KEY environment variable is required when using Chroma Cloud"
            )
        return v

    def create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)

    @property
    def max_file_size_bytes(self) -> int:
        """
        Get maximum file size in bytes.

        Returns:
            int: Maximum file size in bytes.
        """
        return int(self.max_file_size_mb * 1024 * 1024)


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Application settings.
    """
    settings = Settings()
    settings.create_directories()
    return settings
