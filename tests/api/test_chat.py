"""
Tests for chat API endpoint.
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.models.schemas import ChatResponse


def test_chat_endpoint_success(test_client):
    """
    Test successful chat endpoint request.

    Args:
        test_client: FastAPI test client fixture.
    """
    mock_response = ChatResponse(
        success=True,
        answer="Paris is the capital of France.",
        sources=["france_info.pdf"],
        retrieved_chunks=[],
        query_time_ms=200.0,
        session_id=None,
        error=None,
    )

    with patch(
        "app.services.query_service.QueryService.process_chat_query",
        new=AsyncMock(return_value=mock_response),
    ):
        response = test_client.post(
            "/api/v1/chat", json={"query": "What is the capital of France?", "top_k": 5}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["answer"] == "Paris is the capital of France."
        assert "france_info.pdf" in data["sources"]


def test_chat_endpoint_with_filters(test_client):
    """
    Test chat endpoint with metadata filters.

    Args:
        test_client: FastAPI test client fixture.
    """
    mock_response = ChatResponse(
        success=True,
        answer="Filtered answer",
        sources=["doc.pdf"],
        retrieved_chunks=[],
        query_time_ms=150.0,
        session_id="test_session",
        error=None,
    )

    with patch(
        "app.services.query_service.QueryService.process_chat_query",
        new=AsyncMock(return_value=mock_response),
    ):
        response = test_client.post(
            "/api/v1/chat",
            json={
                "query": "Test query",
                "top_k": 10,
                "filter_metadata": {"source_type": "pdf"},
                "session_id": "test_session",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["session_id"] == "test_session"


def test_chat_endpoint_validation_error(test_client):
    """
    Test chat endpoint with invalid request data.

    Args:
        test_client: FastAPI test client fixture.
    """
    # Empty query should fail validation
    response = test_client.post("/api/v1/chat", json={"query": ""})

    assert response.status_code == 422  # Unprocessable Entity


def test_chat_endpoint_query_too_long(test_client):
    """
    Test chat endpoint with query exceeding max length.

    Args:
        test_client: FastAPI test client fixture.
    """
    long_query = "x" * 2001  # Exceeds 2000 char limit

    response = test_client.post("/api/v1/chat", json={"query": long_query})

    assert response.status_code == 422


def test_chat_endpoint_invalid_top_k(test_client):
    """
    Test chat endpoint with invalid top_k values.

    Args:
        test_client: FastAPI test client fixture.
    """
    # top_k too low
    response = test_client.post("/api/v1/chat", json={"query": "Test", "top_k": 0})
    assert response.status_code == 422

    # top_k too high
    response = test_client.post("/api/v1/chat", json={"query": "Test", "top_k": 21})
    assert response.status_code == 422


def test_chat_endpoint_no_results(test_client):
    """
    Test chat endpoint when no documents are found.

    Args:
        test_client: FastAPI test client fixture.
    """
    mock_response = ChatResponse(
        success=True,
        answer="I don't have enough information to answer this question.",
        sources=[],
        retrieved_chunks=[],
        query_time_ms=100.0,
        session_id=None,
        error=None,
    )

    with patch(
        "app.services.query_service.QueryService.process_chat_query",
        new=AsyncMock(return_value=mock_response),
    ):
        response = test_client.post("/api/v1/chat", json={"query": "Unknown topic"})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["sources"]) == 0


def test_chat_endpoint_error_response(test_client):
    """
    Test chat endpoint error handling.

    Args:
        test_client: FastAPI test client fixture.
    """
    mock_response = ChatResponse(
        success=False,
        answer="Error processing query.",
        sources=[],
        retrieved_chunks=[],
        query_time_ms=0,
        session_id=None,
        error="Internal processing error",
    )

    with patch(
        "app.services.query_service.QueryService.process_chat_query",
        new=AsyncMock(return_value=mock_response),
    ):
        response = test_client.post("/api/v1/chat", json={"query": "Test query"})

        assert response.status_code == 200  # Always returns 200, error in body
        data = response.json()
        assert data["success"] is False
        assert data["error"] is not None
