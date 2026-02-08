"""
Tests for query agent.
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.agents.query.agent import QueryAgent
from app.core.config import Settings


@pytest.mark.asyncio
async def test_query_agent_process_query_success(test_settings: Settings):
    """
    Test successful query processing through agent.

    Args:
        test_settings (Settings): Test settings fixture.
    """
    agent = QueryAgent(test_settings)

    mock_result = {
        "success": True,
        "answer": "Test answer",
        "retrieved_chunks": [],
        "query_time_ms": 200.0,
    }

    with patch("app.agents.query.agent.retrieve_and_answer_tool", new=AsyncMock(return_value=mock_result)):
        result = await agent.process_query("What is the document about?")

        assert result["success"] is True
        assert result["answer"] == "Test answer"
        assert "query_time_ms" in result


@pytest.mark.asyncio
async def test_query_agent_process_query_with_params(test_settings: Settings):
    """
    Test query agent with custom parameters.

    Args:
        test_settings (Settings): Test settings fixture.
    """
    agent = QueryAgent(test_settings)

    mock_result = {
        "success": True,
        "answer": "Detailed answer",
        "retrieved_chunks": [],
        "query_time_ms": 250.0,
    }

    with patch("app.agents.query.agent.retrieve_and_answer_tool", new=AsyncMock(return_value=mock_result)) as mock_tool:
        result = await agent.process_query(
            query="Detailed question",
            top_k=10,
            filter_metadata={"source_type": "txt"},
            session_id="test123",
        )

        assert result["success"] is True
        # Verify tool was called with correct parameters
        mock_tool.assert_called_once()
        call_kwargs = mock_tool.call_args.kwargs
        assert call_kwargs["query"] == "Detailed question"
        assert call_kwargs["top_k"] == 10
        assert call_kwargs["session_id"] == "test123"


@pytest.mark.asyncio
async def test_query_agent_error_handling(test_settings: Settings):
    """
    Test query agent error handling.

    Args:
        test_settings (Settings): Test settings fixture.
    """
    agent = QueryAgent(test_settings)

    with patch(
        "app.agents.query.agent.retrieve_and_answer_tool",
        new=AsyncMock(side_effect=Exception("Tool error")),
    ):
        result = await agent.process_query("Test query")

        assert result["success"] is False
        assert "error" in result
