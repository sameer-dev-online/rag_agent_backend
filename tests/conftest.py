"""
Pytest configuration and fixtures.
"""

import pytest
from pathlib import Path
from typing import List
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.constants import VectorStoreType, EmbeddingProvider
from app.models.document import Document, DocumentChunk, DocumentMetadata
from app.rag.embeddings.base import BaseEmbedder
from app.rag.storage.base import BaseVectorStore


@pytest.fixture
def test_settings() -> Settings:
    """
    Create test settings with overrides.

    Returns:
        Settings: Test configuration.
    """
    return Settings(
        debug=True,
        log_level="DEBUG",
        embedding_provider="local",
        vector_store="memory",
        max_file_size_mb=5,
        max_files_per_request=5,
    )


@pytest.fixture
def test_settings_local() -> Settings:
    """
    Test settings for local ChromaDB.

    Returns:
        Settings: Test configuration with local vector store.
    """
    return Settings(
        debug=True,
        vector_store=VectorStoreType.CHROMA_LOCAL,
        chroma_persist_dir=Path("data/test_vector_store"),
        chroma_collection_name="test_documents",
        embedding_provider=EmbeddingProvider.LOCAL,
        openai_api_key=None,
    )


@pytest.fixture
def test_settings_cloud() -> Settings:
    """
    Test settings for Chroma Cloud.

    Returns:
        Settings: Test configuration with cloud vector store.
    """
    return Settings(
        debug=True,
        vector_store=VectorStoreType.CHROMA_CLOUD,
        chroma_cloud_api_key="test-api-key",
        chroma_cloud_host="localhost",
        chroma_cloud_port=8000,
        chroma_collection_name="test_documents",
        embedding_provider=EmbeddingProvider.LOCAL,
        openai_api_key=None,
    )


@pytest.fixture
def test_client():
    """
    Create FastAPI test client.

    Returns:
        TestClient: FastAPI test client.
    """
    from main import app

    return TestClient(app)


@pytest.fixture
def sample_document() -> Document:
    """
    Create a sample document for testing.

    Returns:
        Document: Sample document.
    """
    metadata = DocumentMetadata(
        filename="test.txt",
        file_size_bytes=1024,
        file_hash="abc123",
        source_type="txt",
    )
    return Document(
        content="This is a test document with sample content for testing purposes.",
        metadata=metadata,
    )


@pytest.fixture
def sample_pdf_path(tmp_path: Path) -> Path:
    """
    Create a sample PDF file for testing.

    Args:
        tmp_path (Path): Pytest temporary directory.

    Returns:
        Path: Path to sample PDF.
    """
    # Create a simple text file (for testing purposes)
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("Sample PDF content")
    return pdf_path


@pytest.fixture
def sample_txt_path(tmp_path: Path) -> Path:
    """
    Create a sample text file for testing.

    Args:
        tmp_path (Path): Pytest temporary directory.

    Returns:
        Path: Path to sample text file.
    """
    txt_path = tmp_path / "test.txt"
    txt_path.write_text("Sample text content for testing.")
    return txt_path


@pytest.fixture
def mock_embedder() -> BaseEmbedder:
    """
    Create a mock embedder for testing.

    Returns:
        BaseEmbedder: Mock embedder.
    """
    embedder = MagicMock(spec=BaseEmbedder)
    embedder.embedding_dimensions = 384

    async def mock_embed_chunks(chunks):
        for chunk in chunks:
            chunk.embedding = [0.1] * 384
        return chunks

    async def mock_embed_query(query):
        return [0.1] * 384

    embedder.embed_chunks = mock_embed_chunks
    embedder.embed_query = mock_embed_query

    return embedder


@pytest.fixture
def mock_vector_store() -> BaseVectorStore:
    """
    Create a mock vector store for testing.

    Returns:
        BaseVectorStore: Mock vector store.
    """
    store = MagicMock(spec=BaseVectorStore)
    store.chunks = []

    async def mock_add_chunks(chunks):
        store.chunks.extend(chunks)

    async def mock_count():
        return len(store.chunks)

    store.add_chunks = mock_add_chunks
    store.count = mock_count

    return store


@pytest.fixture
def sample_chunks(sample_document: Document) -> List[DocumentChunk]:
    """
    Create sample document chunks for testing.

    Args:
        sample_document (Document): Sample document fixture.

    Returns:
        List[DocumentChunk]: List of test chunks with embeddings.
    """
    document_id = str(uuid4())
    chunks = []

    for i in range(3):
        chunk = DocumentChunk(
            id=str(uuid4()),
            document_id=document_id,
            content=f"This is test chunk {i} with some sample content.",
            chunk_index=i,
            metadata=sample_document.metadata,
            embedding=[0.1 * j for j in range(384)],  # Sample embedding vector
        )
        chunks.append(chunk)

    return chunks


@pytest.fixture
def sample_query_embedding() -> List[float]:
    """
    Sample query embedding for testing.

    Returns:
        List[float]: Sample embedding vector.
    """
    return [0.1 * i for i in range(384)]
