"""
Constants and enums for the RAG application.
"""

from enum import Enum


class FileType(str, Enum):
    """Supported file types for document ingestion."""

    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"


class EmbeddingProvider(str, Enum):
    """Supported embedding providers."""

    OPENAI = "openai"
    LOCAL = "local"


class VectorStoreType(str, Enum):
    """Supported vector store types."""

    CHROMA_LOCAL = "chroma_local"
    CHROMA_CLOUD = "chroma_cloud"
    MEMORY = "memory"


class ProcessingStatus(str, Enum):
    """Document processing status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# Default values
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_MAX_FILE_SIZE_MB = 10
DEFAULT_MAX_FILES_PER_REQUEST = 10

# OpenAI defaults
DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_OPENAI_EMBEDDING_DIMENSIONS = 1536

# Local embedding defaults
DEFAULT_LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ChromaDB defaults
DEFAULT_CHROMA_COLLECTION_NAME = "documents"

# Chroma Cloud defaults
DEFAULT_CHROMA_CLOUD_HOST = "api.trychroma.com"
DEFAULT_CHROMA_CLOUD_PORT = 443

# Query/Chat defaults
DEFAULT_QUERY_TOP_K = 5
DEFAULT_QUERY_LLM_MODEL = "gpt-4o-mini"
DEFAULT_QUERY_TEMPERATURE = 0.0
DEFAULT_MAX_CONTEXT_LENGTH = 4000

# Supported file extensions
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx"}

# MIME type mapping
MIME_TYPE_MAPPING = {
    "application/pdf": FileType.PDF,
    "text/plain": FileType.TXT,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": FileType.DOCX,
}
