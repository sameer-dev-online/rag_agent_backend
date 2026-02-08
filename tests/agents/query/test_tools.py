"""
Tests for query agent tools.
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.agents.query.tools import retrieve_and_answer_tool
from app.core.config import Settings
from app.models.document import DocumentChunk, DocumentMetadata


@pytest.mark.asyncio
async def test_retrieve_and_answer_tool_success(test_settings: Settings):
    """
    Test successful query processing through retrieve_and_answer_tool.

    Args:
        test_settings (Settings): Test settings fixture.
    """
    # Mock pipeline result
    mock_result = {
        "answer": "Test answer based on documents.",
        "retrieved_chunks": [],
        "query_time_ms": 150.0,
        "status": "completed",
    }

    with patch("app.agents.query.tools.QueryPipeline") as mock_pipeline_class:
        mock_pipeline = AsyncMock()
        mock_pipeline.process_query = AsyncMock(return_value=mock_result)
        mock_pipeline_class.return_value = mock_pipeline

        result = await retrieve_and_answer_tool(
            query="What is the main topic?",
            settings=test_settings,
            top_k=5,
        )

        assert result["success"] is True
        assert result["answer"] == "Test answer based on documents."
        assert result["query_time_ms"] == 150.0


@pytest.mark.asyncio
async def test_retrieve_and_answer_tool_error(test_settings: Settings):
    """
    Test error handling in retrieve_and_answer_tool.

    Args:
        test_settings (Settings): Test settings fixture.
    """
    with patch("app.agents.query.tools.QueryPipeline") as mock_pipeline_class:
        mock_pipeline = AsyncMock()
        mock_pipeline.process_query = AsyncMock(side_effect=Exception("Test error"))
        mock_pipeline_class.return_value = mock_pipeline

        result = await retrieve_and_answer_tool(
            query="What is the main topic?",
            settings=test_settings,
        )

        assert result["success"] is False
        assert "error" in result
        assert result["answer"] == "Error processing query. Please try again."


@pytest.mark.asyncio
async def test_retrieve_and_answer_tool_with_metadata_filter(test_settings: Settings):
    """
    Test query with metadata filters.

    Args:
        test_settings (Settings): Test settings fixture.
    """
    mock_result = {
        "answer": "Filtered answer.",
        "retrieved_chunks": [],
        "query_time_ms": 100.0,
        "status": "completed",
    }

    with patch("app.agents.query.tools.QueryPipeline") as mock_pipeline_class:
        mock_pipeline = AsyncMock()
        mock_pipeline.process_query = AsyncMock(return_value=mock_result)
        mock_pipeline_class.return_value = mock_pipeline

        result = await retrieve_and_answer_tool(
            query="Test query",
            settings=test_settings,
            filter_metadata={"source_type": "pdf"},
        )

        assert result["success"] is True
        mock_pipeline.process_query.assert_called_once()
