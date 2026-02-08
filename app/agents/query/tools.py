"""
Tools for query agent.
"""

from typing import Dict, Optional

from app.core.config import Settings
from app.core.logging import get_logger
from app.rag.pipelines.query import QueryPipeline

logger = get_logger(__name__)


async def retrieve_and_answer_tool(
    query: str,
    settings: Settings,
    top_k: Optional[int] = None,
    filter_metadata: Optional[dict] = None,
    session_id: Optional[str] = None,
) -> Dict:
    """
    Retrieve relevant documents and generate answer.

    This tool processes a user query through the complete RAG pipeline:
    1. Generate query embedding
    2. Retrieve relevant chunks from vector store
    3. Format context with source attribution
    4. Generate grounded answer using LLM

    Args:
        query (str): User query text.
        settings (Settings): Application settings.
        top_k (Optional[int]): Number of chunks to retrieve.
        filter_metadata (Optional[dict]): Metadata filters for retrieval.
        session_id (Optional[str]): Session ID for conversation tracking.

    Returns:
        Dict: Result containing success status, answer, retrieved chunks, and timing.
    """
    try:
        logger.info(f"Processing query through RAG pipeline: {query[:100]}")

        # Create pipeline and process query
        pipeline = QueryPipeline(settings)
        result = await pipeline.process_query(query, top_k, filter_metadata, session_id)

        logger.info(f"Query processed successfully: {result['query_time_ms']:.2f}ms")

        return {
            "success": True,
            **result,
        }

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return {
            "success": False,
            "error": str(e),
            "answer": "Error processing query. Please try again.",
            "retrieved_chunks": [],
            "query_time_ms": 0,
        }
