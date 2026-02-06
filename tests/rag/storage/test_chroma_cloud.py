"""
Unit tests for ChromaCloudVectorStore.
"""

from typing import List
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.core.config import Settings
from app.core.errors import VectorStoreError
from app.models.document import DocumentChunk
from app.rag.storage.chroma_cloud import ChromaCloudVectorStore


class TestChromaCloudVectorStore:
    """Test cases for ChromaCloudVectorStore."""

    @patch("app.rag.storage.chroma_cloud.chromadb.HttpClient")
    def test_initialization_success(
        self, mock_http_client: MagicMock, test_settings_cloud: Settings
    ):
        """
        Test successful initialization of Chroma Cloud vector store.

        Args:
            mock_http_client (MagicMock): Mocked HttpClient.
            test_settings_cloud (Settings): Test settings fixture.
        """
        # Arrange
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_http_client.return_value = mock_client

        # Act
        store = ChromaCloudVectorStore(test_settings_cloud)

        # Assert
        assert store.client == mock_client
        assert store.collection == mock_collection
        mock_http_client.assert_called_once()
        mock_client.get_or_create_collection.assert_called_once_with(
            name=test_settings_cloud.chroma_collection_name,
            metadata={"description": "RAG document chunks"},
        )

    @patch("app.rag.storage.chroma_cloud.chromadb.HttpClient")
    def test_initialization_with_tenant_and_database(
        self, mock_http_client: MagicMock, test_settings_cloud: Settings
    ):
        """
        Test initialization with tenant and database settings.

        Args:
            mock_http_client (MagicMock): Mocked HttpClient.
            test_settings_cloud (Settings): Test settings fixture.
        """
        # Arrange
        test_settings_cloud.chroma_cloud_tenant = "test-tenant"
        test_settings_cloud.chroma_cloud_database = "test-database"
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_http_client.return_value = mock_client

        # Act
        store = ChromaCloudVectorStore(test_settings_cloud)

        # Assert
        mock_client.set_tenant.assert_called_once_with("test-tenant")
        mock_client.set_database.assert_called_once_with("test-database")

    @patch("app.rag.storage.chroma_cloud.chromadb.HttpClient")
    def test_initialization_failure(
        self, mock_http_client: MagicMock, test_settings_cloud: Settings
    ):
        """
        Test initialization failure handling.

        Args:
            mock_http_client (MagicMock): Mocked HttpClient.
            test_settings_cloud (Settings): Test settings fixture.
        """
        # Arrange
        mock_http_client.side_effect = Exception("Connection failed")

        # Act & Assert
        with pytest.raises(VectorStoreError) as exc_info:
            ChromaCloudVectorStore(test_settings_cloud)

        assert "Failed to initialize Chroma Cloud" in str(exc_info.value)
        assert "Connection failed" in str(exc_info.value)

    @patch("app.rag.storage.chroma_cloud.chromadb.HttpClient")
    @pytest.mark.asyncio
    async def test_add_chunks_success(
        self,
        mock_http_client: MagicMock,
        test_settings_cloud: Settings,
        sample_chunks: List[DocumentChunk],
    ):
        """
        Test successful addition of chunks.

        Args:
            mock_http_client (MagicMock): Mocked HttpClient.
            test_settings_cloud (Settings): Test settings fixture.
            sample_chunks (List[DocumentChunk]): Sample chunks fixture.
        """
        # Arrange
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_http_client.return_value = mock_client

        store = ChromaCloudVectorStore(test_settings_cloud)

        # Act
        await store.add_chunks(sample_chunks)

        # Assert
        mock_collection.add.assert_called_once()
        call_kwargs = mock_collection.add.call_args.kwargs
        assert len(call_kwargs["ids"]) == 3
        assert len(call_kwargs["embeddings"]) == 3
        assert len(call_kwargs["documents"]) == 3
        assert len(call_kwargs["metadatas"]) == 3

    @patch("app.rag.storage.chroma_cloud.chromadb.HttpClient")
    @pytest.mark.asyncio
    async def test_add_chunks_empty_list(
        self, mock_http_client: MagicMock, test_settings_cloud: Settings
    ):
        """
        Test adding empty list of chunks.

        Args:
            mock_http_client (MagicMock): Mocked HttpClient.
            test_settings_cloud (Settings): Test settings fixture.
        """
        # Arrange
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_http_client.return_value = mock_client

        store = ChromaCloudVectorStore(test_settings_cloud)

        # Act
        await store.add_chunks([])

        # Assert
        mock_collection.add.assert_not_called()

    @patch("app.rag.storage.chroma_cloud.chromadb.HttpClient")
    @pytest.mark.asyncio
    async def test_add_chunks_failure(
        self,
        mock_http_client: MagicMock,
        test_settings_cloud: Settings,
        sample_chunks: List[DocumentChunk],
    ):
        """
        Test add_chunks failure handling.

        Args:
            mock_http_client (MagicMock): Mocked HttpClient.
            test_settings_cloud (Settings): Test settings fixture.
            sample_chunks (List[DocumentChunk]): Sample chunks fixture.
        """
        # Arrange
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.add.side_effect = Exception("Storage error")
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_http_client.return_value = mock_client

        store = ChromaCloudVectorStore(test_settings_cloud)

        # Act & Assert
        with pytest.raises(VectorStoreError) as exc_info:
            await store.add_chunks(sample_chunks)

        assert "Failed to add chunks to Chroma Cloud" in str(exc_info.value)

    @patch("app.rag.storage.chroma_cloud.chromadb.HttpClient")
    @pytest.mark.asyncio
    async def test_similarity_search_success(
        self,
        mock_http_client: MagicMock,
        test_settings_cloud: Settings,
        sample_query_embedding: List[float],
        sample_chunks: List[DocumentChunk],
    ):
        """
        Test successful similarity search.

        Args:
            mock_http_client (MagicMock): Mocked HttpClient.
            test_settings_cloud (Settings): Test settings fixture.
            sample_query_embedding (List[float]): Query embedding fixture.
            sample_chunks (List[DocumentChunk]): Sample chunks fixture.
        """
        # Arrange
        mock_client = MagicMock()
        mock_collection = MagicMock()

        # Mock query results
        chunk = sample_chunks[0]
        mock_collection.query.return_value = {
            "ids": [[str(chunk.id)]],
            "documents": [[chunk.content]],
            "metadatas": [
                [
                    {
                        "document_id": str(chunk.document_id),
                        "chunk_index": chunk.chunk_index,
                        "filename": chunk.metadata.filename,
                        "file_hash": chunk.metadata.file_hash,
                        "source_type": chunk.metadata.source_type,
                    }
                ]
            ],
            "embeddings": [[chunk.embedding]],
        }

        mock_client.get_or_create_collection.return_value = mock_collection
        mock_http_client.return_value = mock_client

        store = ChromaCloudVectorStore(test_settings_cloud)

        # Act
        results = await store.similarity_search(sample_query_embedding, k=1)

        # Assert
        assert len(results) == 1
        assert results[0].id == str(chunk.id)
        assert results[0].content == chunk.content
        mock_collection.query.assert_called_once()

    @patch("app.rag.storage.chroma_cloud.chromadb.HttpClient")
    @pytest.mark.asyncio
    async def test_similarity_search_empty_results(
        self,
        mock_http_client: MagicMock,
        test_settings_cloud: Settings,
        sample_query_embedding: List[float],
    ):
        """
        Test similarity search with no results.

        Args:
            mock_http_client (MagicMock): Mocked HttpClient.
            test_settings_cloud (Settings): Test settings fixture.
            sample_query_embedding (List[float]): Query embedding fixture.
        """
        # Arrange
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"ids": [[]], "documents": [[]], "metadatas": [[]]}

        mock_client.get_or_create_collection.return_value = mock_collection
        mock_http_client.return_value = mock_client

        store = ChromaCloudVectorStore(test_settings_cloud)

        # Act
        results = await store.similarity_search(sample_query_embedding, k=5)

        # Assert
        assert len(results) == 0

    @patch("app.rag.storage.chroma_cloud.chromadb.HttpClient")
    @pytest.mark.asyncio
    async def test_similarity_search_failure(
        self,
        mock_http_client: MagicMock,
        test_settings_cloud: Settings,
        sample_query_embedding: List[float],
    ):
        """
        Test similarity search failure handling.

        Args:
            mock_http_client (MagicMock): Mocked HttpClient.
            test_settings_cloud (Settings): Test settings fixture.
            sample_query_embedding (List[float]): Query embedding fixture.
        """
        # Arrange
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.query.side_effect = Exception("Query failed")
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_http_client.return_value = mock_client

        store = ChromaCloudVectorStore(test_settings_cloud)

        # Act & Assert
        with pytest.raises(VectorStoreError) as exc_info:
            await store.similarity_search(sample_query_embedding)

        assert "Failed to search Chroma Cloud" in str(exc_info.value)

    @patch("app.rag.storage.chroma_cloud.chromadb.HttpClient")
    @pytest.mark.asyncio
    async def test_delete_by_document_id_success(
        self, mock_http_client: MagicMock, test_settings_cloud: Settings
    ):
        """
        Test successful deletion by document ID.

        Args:
            mock_http_client (MagicMock): Mocked HttpClient.
            test_settings_cloud (Settings): Test settings fixture.
        """
        # Arrange
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_http_client.return_value = mock_client

        store = ChromaCloudVectorStore(test_settings_cloud)
        document_id = str(uuid4())

        # Act
        await store.delete_by_document_id(document_id)

        # Assert
        mock_collection.delete.assert_called_once_with(where={"document_id": document_id})

    @patch("app.rag.storage.chroma_cloud.chromadb.HttpClient")
    @pytest.mark.asyncio
    async def test_delete_by_document_id_failure(
        self, mock_http_client: MagicMock, test_settings_cloud: Settings
    ):
        """
        Test delete failure handling.

        Args:
            mock_http_client (MagicMock): Mocked HttpClient.
            test_settings_cloud (Settings): Test settings fixture.
        """
        # Arrange
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.delete.side_effect = Exception("Delete failed")
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_http_client.return_value = mock_client

        store = ChromaCloudVectorStore(test_settings_cloud)
        document_id = str(uuid4())

        # Act & Assert
        with pytest.raises(VectorStoreError) as exc_info:
            await store.delete_by_document_id(document_id)

        assert "Failed to delete document from Chroma Cloud" in str(exc_info.value)

    @patch("app.rag.storage.chroma_cloud.chromadb.HttpClient")
    @pytest.mark.asyncio
    async def test_count_success(
        self, mock_http_client: MagicMock, test_settings_cloud: Settings
    ):
        """
        Test successful count operation.

        Args:
            mock_http_client (MagicMock): Mocked HttpClient.
            test_settings_cloud (Settings): Test settings fixture.
        """
        # Arrange
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 42
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_http_client.return_value = mock_client

        store = ChromaCloudVectorStore(test_settings_cloud)

        # Act
        count = await store.count()

        # Assert
        assert count == 42
        mock_collection.count.assert_called_once()

    @patch("app.rag.storage.chroma_cloud.chromadb.HttpClient")
    @pytest.mark.asyncio
    async def test_count_failure(
        self, mock_http_client: MagicMock, test_settings_cloud: Settings
    ):
        """
        Test count failure handling.

        Args:
            mock_http_client (MagicMock): Mocked HttpClient.
            test_settings_cloud (Settings): Test settings fixture.
        """
        # Arrange
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.side_effect = Exception("Count failed")
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_http_client.return_value = mock_client

        store = ChromaCloudVectorStore(test_settings_cloud)

        # Act & Assert
        with pytest.raises(VectorStoreError) as exc_info:
            await store.count()

        assert "Failed to count chunks in Chroma Cloud" in str(exc_info.value)

    def test_missing_api_key(self, test_settings_cloud: Settings):
        """
        Test configuration validation for missing API key.

        Args:
            test_settings_cloud (Settings): Test settings fixture.
        """
        # Act & Assert
        with pytest.raises(Exception):
            # This should fail during Settings creation, not during store initialization
            Settings(
                debug=True,
                vector_store="chroma_cloud",
                chroma_cloud_api_key=None,  # Missing API key
            )
