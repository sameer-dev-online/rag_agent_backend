"""
Query agent using PydanticAI.
"""

from typing import Dict, Optional

from pydantic_ai import Agent

from app.core.config import Settings
from app.core.logging import get_logger

from .prompts import QUERY_AGENT_SYSTEM_PROMPT
from .tools import retrieve_and_answer_tool

logger = get_logger(__name__)


class QueryAgent:
    """
    Query agent for RAG retrieval and answer generation.

    This agent orchestrates the query processing workflow using PydanticAI.
    """

    def __init__(self, settings: Settings):
        """
        Initialize query agent.

        Args:
            settings (Settings): Application settings.
        """
        self.settings = settings
        self.agent = Agent(
            model=f"openai:{settings.query_llm_model}",
            system_prompt=QUERY_AGENT_SYSTEM_PROMPT,
        )

    async def process_query(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[dict] = None,
        session_id: Optional[str] = None,
    ) -> Dict:
        """
        Process query through RAG system.

        Args:
            query (str): User query text.
            top_k (Optional[int]): Number of chunks to retrieve.
            filter_metadata (Optional[dict]): Metadata filters for retrieval.
            session_id (Optional[str]): Session ID for conversation tracking.

        Returns:
            Dict: Query results including success status, answer, and retrieved chunks.
        """
        try:
            logger.info(f"Query agent processing: {query[:100]}")

            # Call tool directly (simplified agent pattern)
            # Reason: For simple RAG queries, direct tool invocation is more efficient
            # than full agent reasoning loop
            result = await retrieve_and_answer_tool(
                query=query,
                settings=self.settings,
                top_k=top_k,
                filter_metadata=filter_metadata,
                session_id=session_id,
            )

            logger.info(f"Query agent completed: success={result.get('success', False)}")

            return result

        except Exception as e:
            logger.error(f"Query agent error: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": "Error processing query.",
                "retrieved_chunks": [],
                "query_time_ms": 0,
            }
