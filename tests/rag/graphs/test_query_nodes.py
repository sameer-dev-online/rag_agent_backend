"""
Tests for query workflow nodes.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.models.document import DocumentChunk, DocumentMetadata
from app.rag.graphs.query_nodes import (
    embed_query_node,
    format_context_node,
    generate_answer_node,
    retrieve_chunks_node,
)
from app.rag.graphs.query_state import QueryState


@pytest.mark.asyncio
async def test_embed_query_node_success():
    """Test successful query embedding generation."""
    state: QueryState = {
        "query": "What is machine learning?",
        "top_k": 5,
        "filter_metadata": None,
        "session_id": None,
        "query_embedding": None,
        "retrieved_chunks": None,
        "context": None,
        "answer": None,
        "query_start_time": 0.0,
        "query_end_time": None,
        "errors": [],
        "status": "pending",
    }

    mock_embedder = MagicMock()
    mock_embedder.embed_query = AsyncMock(return_value=[0.1, 0.2, 0.3])

    result = await embed_query_node(state, mock_embedder)

    assert result["status"] == "embedding_complete"
    assert result["query_embedding"] == [0.1, 0.2, 0.3]
    mock_embedder.embed_query.assert_called_once_with("What is machine learning?")


@pytest.mark.asyncio
async def test_embed_query_node_error():
    """Test error handling in embedding node."""
    state: QueryState = {
        "query": "Test query",
        "top_k": 5,
        "filter_metadata": None,
        "session_id": None,
        "query_embedding": None,
        "retrieved_chunks": None,
        "context": None,
        "answer": None,
        "query_start_time": 0.0,
        "query_end_time": None,
        "errors": [],
        "status": "pending",
    }

    mock_embedder = MagicMock()
    mock_embedder.embed_query = AsyncMock(side_effect=Exception("Embedding failed"))

    result = await embed_query_node(state, mock_embedder)

    assert result["status"] == "failed"
    assert len(result["errors"]) > 0


@pytest.mark.asyncio
async def test_retrieve_chunks_node_success(sample_document):
    """Test successful chunk retrieval."""
    # Create mock chunks
    chunk = DocumentChunk(
        id=uuid4(),
        document_id=sample_document.id,
        content="Sample chunk content",
        chunk_index=0,
        metadata=sample_document.metadata,
    )

    state: QueryState = {
        "query": "Test query",
        "top_k": 5,
        "filter_metadata": None,
        "session_id": None,
        "query_embedding": [0.1, 0.2, 0.3],
        "retrieved_chunks": None,
        "context": None,
        "answer": None,
        "query_start_time": 0.0,
        "query_end_time": None,
        "errors": [],
        "status": "embedding_complete",
    }

    mock_vector_store = MagicMock()
    mock_vector_store.similarity_search = AsyncMock(return_value=[chunk])

    result = await retrieve_chunks_node(state, mock_vector_store)

    assert result["status"] == "retrieval_complete"
    assert len(result["retrieved_chunks"]) == 1
    assert result["retrieved_chunks"][0].content == "Sample chunk content"


@pytest.mark.asyncio
async def test_format_context_node_with_chunks(sample_document):
    """Test context formatting with retrieved chunks."""
    chunk = DocumentChunk(
        id=uuid4(),
        document_id=sample_document.id,
        content="This is test content",
        chunk_index=0,
        metadata=DocumentMetadata(
            filename="test.pdf",
            file_size_bytes=100,
            file_hash="abc",
            source_type="pdf",
        ),
    )

    state: QueryState = {
        "query": "Test",
        "top_k": 5,
        "filter_metadata": None,
        "session_id": None,
        "query_embedding": [0.1],
        "retrieved_chunks": [chunk],
        "context": None,
        "answer": None,
        "query_start_time": 0.0,
        "query_end_time": None,
        "errors": [],
        "status": "retrieval_complete",
    }

    result = await format_context_node(state, max_length=5000)

    assert result["status"] == "formatting_complete"
    assert "test.pdf" in result["context"]
    assert "This is test content" in result["context"]


@pytest.mark.asyncio
async def test_format_context_node_empty_chunks():
    """Test context formatting with no chunks."""
    state: QueryState = {
        "query": "Test",
        "top_k": 5,
        "filter_metadata": None,
        "session_id": None,
        "query_embedding": [0.1],
        "retrieved_chunks": [],
        "context": None,
        "answer": None,
        "query_start_time": 0.0,
        "query_end_time": None,
        "errors": [],
        "status": "retrieval_complete",
    }

    result = await format_context_node(state, max_length=5000)

    assert result["status"] == "formatting_complete"
    assert result["context"] == ""


@pytest.mark.asyncio
async def test_generate_answer_node_success():
    """Test successful answer generation."""
    state: QueryState = {
        "query": "What is AI?",
        "top_k": 5,
        "filter_metadata": None,
        "session_id": None,
        "query_embedding": [0.1],
        "retrieved_chunks": [],
        "context": "[Document 1: test.pdf]\nAI is artificial intelligence.",
        "answer": None,
        "query_start_time": 0.0,
        "query_end_time": None,
        "errors": [],
        "status": "formatting_complete",
    }

    mock_llm_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="AI is artificial intelligence."))]
    mock_llm_client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = await generate_answer_node(state, mock_llm_client, "gpt-4o-mini", 0.0)

    assert result["status"] == "completed"
    assert result["answer"] == "AI is artificial intelligence."
    assert "query_end_time" in result
