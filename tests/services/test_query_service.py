"""
Tests for query service.
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.core.config import Settings
from app.models.document import DocumentChunk, DocumentMetadata
from app.models.schemas import ChatRequest
from app.services.query_service import QueryService


@pytest.mark.asyncio
async def test_query_service_success(test_settings: Settings, sample_document):
    """
    Test successful query service processing.

    Args:
        test_settings (Settings): Test settings fixture.
        sample_document: Sample document fixture.
    """
    service = QueryService(test_settings)

    # Create mock chunk
    chunk = DocumentChunk(
        id=uuid4(),
        document_id=sample_document.id,
        content="Test content about AI",
        chunk_index=0,
        metadata=DocumentMetadata(
            filename="ai_paper.pdf",
            file_size_bytes=1000,
            file_hash="hash123",
            source_type="pdf",
        ),
    )

    mock_agent_result = {
        "success": True,
        "answer": "AI stands for Artificial Intelligence.",
        "retrieved_chunks": [chunk],
        "query_time_ms": 250.0,
    }

    with patch.object(service.query_agent, "process_query", new=AsyncMock(return_value=mock_agent_result)):
        request = ChatRequest(query="What is AI?", top_k=5)
        response = await service.process_chat_query(request)

        assert response.success is True
        assert response.answer == "AI stands for Artificial Intelligence."
        assert len(response.sources) == 1
        assert "ai_paper.pdf" in response.sources
        assert len(response.retrieved_chunks) == 1
        assert response.retrieved_chunks[0].filename == "ai_paper.pdf"
        assert response.query_time_ms == 250.0


@pytest.mark.asyncio
async def test_query_service_multiple_sources(test_settings: Settings, sample_document):
    """
    Test query service with multiple source documents.

    Args:
        test_settings (Settings): Test settings fixture.
        sample_document: Sample document fixture.
    """
    service = QueryService(test_settings)

    # Create mock chunks from different files
    chunks = [
        DocumentChunk(
            id=uuid4(),
            document_id=sample_document.id,
            content="Content from doc1",
            chunk_index=0,
            metadata=DocumentMetadata(
                filename="doc1.pdf",
                file_size_bytes=1000,
                file_hash="hash1",
                source_type="pdf",
            ),
        ),
        DocumentChunk(
            id=uuid4(),
            document_id=sample_document.id,
            content="Content from doc2",
            chunk_index=0,
            metadata=DocumentMetadata(
                filename="doc2.txt",
                file_size_bytes=500,
                file_hash="hash2",
                source_type="txt",
            ),
        ),
        DocumentChunk(
            id=uuid4(),
            document_id=sample_document.id,
            content="Another from doc1",
            chunk_index=1,
            metadata=DocumentMetadata(
                filename="doc1.pdf",
                file_size_bytes=1000,
                file_hash="hash1",
                source_type="pdf",
            ),
        ),
    ]

    mock_agent_result = {
        "success": True,
        "answer": "Combined answer from multiple documents.",
        "retrieved_chunks": chunks,
        "query_time_ms": 300.0,
    }

    with patch.object(service.query_agent, "process_query", new=AsyncMock(return_value=mock_agent_result)):
        request = ChatRequest(query="Multi-doc query")
        response = await service.process_chat_query(request)

        assert response.success is True
        # Should have 2 unique sources
        assert len(response.sources) == 2
        assert "doc1.pdf" in response.sources
        assert "doc2.txt" in response.sources
        # Should have 3 chunks
        assert len(response.retrieved_chunks) == 3


@pytest.mark.asyncio
async def test_query_service_no_chunks(test_settings: Settings):
    """
    Test query service when no chunks are retrieved.

    Args:
        test_settings (Settings): Test settings fixture.
    """
    service = QueryService(test_settings)

    mock_agent_result = {
        "success": True,
        "answer": "I don't have enough information to answer this question.",
        "retrieved_chunks": [],
        "query_time_ms": 100.0,
    }

    with patch.object(service.query_agent, "process_query", new=AsyncMock(return_value=mock_agent_result)):
        request = ChatRequest(query="Obscure query")
        response = await service.process_chat_query(request)

        assert response.success is True
        assert len(response.sources) == 0
        assert len(response.retrieved_chunks) == 0


@pytest.mark.asyncio
async def test_query_service_error_handling(test_settings: Settings):
    """
    Test query service error handling.

    Args:
        test_settings (Settings): Test settings fixture.
    """
    service = QueryService(test_settings)

    with patch.object(
        service.query_agent, "process_query", new=AsyncMock(side_effect=Exception("Agent error"))
    ):
        request = ChatRequest(query="Test query")
        response = await service.process_chat_query(request)

        assert response.success is False
        assert response.error is not None
        assert len(response.sources) == 0
        assert len(response.retrieved_chunks) == 0


@pytest.mark.asyncio
async def test_query_service_with_session_id(test_settings: Settings):
    """
    Test query service with session ID.

    Args:
        test_settings (Settings): Test settings fixture.
    """
    service = QueryService(test_settings)

    mock_agent_result = {
        "success": True,
        "answer": "Answer with session",
        "retrieved_chunks": [],
        "query_time_ms": 200.0,
    }

    with patch.object(service.query_agent, "process_query", new=AsyncMock(return_value=mock_agent_result)):
        request = ChatRequest(query="Test", session_id="session_abc")
        response = await service.process_chat_query(request)

        assert response.success is True
        assert response.session_id == "session_abc"
