"""
Tests for query pipeline.
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.core.config import Settings
from app.core.errors import DocumentProcessingError
from app.rag.pipelines.query import QueryPipeline


@pytest.mark.asyncio
async def test_query_pipeline_success(test_settings: Settings):
    """
    Test successful query processing through pipeline.

    Args:
        test_settings (Settings): Test settings fixture.
    """
    pipeline = QueryPipeline(test_settings)

    mock_final_state = {
        "query": "Test query",
        "answer": "Test answer from documents",
        "retrieved_chunks": [],
        "query_start_time": 1000.0,
        "query_end_time": 1001.5,
        "status": "completed",
        "errors": [],
    }

    with patch.object(pipeline.graph, "ainvoke", new=AsyncMock(return_value=mock_final_state)):
        result = await pipeline.process_query("Test query", top_k=5)

        assert result["answer"] == "Test answer from documents"
        assert result["status"] == "completed"
        assert result["query_time_ms"] == pytest.approx(1500.0, rel=1)


@pytest.mark.asyncio
async def test_query_pipeline_with_filters(test_settings: Settings):
    """
    Test query pipeline with metadata filters.

    Args:
        test_settings (Settings): Test settings fixture.
    """
    pipeline = QueryPipeline(test_settings)

    mock_final_state = {
        "query": "Filtered query",
        "answer": "Filtered answer",
        "retrieved_chunks": [],
        "query_start_time": 1000.0,
        "query_end_time": 1001.0,
        "status": "completed",
        "errors": [],
    }

    with patch.object(pipeline.graph, "ainvoke", new=AsyncMock(return_value=mock_final_state)) as mock_invoke:
        result = await pipeline.process_query(
            "Filtered query", filter_metadata={"source_type": "pdf"}, session_id="sess123"
        )

        # Verify initial state was set correctly
        call_args = mock_invoke.call_args[0][0]
        assert call_args["filter_metadata"] == {"source_type": "pdf"}
        assert call_args["session_id"] == "sess123"
        assert result["answer"] == "Filtered answer"


@pytest.mark.asyncio
async def test_query_pipeline_failed_status(test_settings: Settings):
    """
    Test query pipeline with failed status.

    Args:
        test_settings (Settings): Test settings fixture.
    """
    pipeline = QueryPipeline(test_settings)

    mock_final_state = {
        "query": "Test query",
        "status": "failed",
        "errors": ["Embedding error", "Retrieval error"],
    }

    with patch.object(pipeline.graph, "ainvoke", new=AsyncMock(return_value=mock_final_state)):
        with pytest.raises(DocumentProcessingError) as exc_info:
            await pipeline.process_query("Test query")

        assert "Query processing failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_query_pipeline_exception(test_settings: Settings):
    """
    Test query pipeline exception handling.

    Args:
        test_settings (Settings): Test settings fixture.
    """
    pipeline = QueryPipeline(test_settings)

    with patch.object(pipeline.graph, "ainvoke", new=AsyncMock(side_effect=Exception("Graph error"))):
        with pytest.raises(DocumentProcessingError) as exc_info:
            await pipeline.process_query("Test query")

        assert "Unexpected error processing query" in str(exc_info.value)
