"""
Query pipeline wrapping LangGraph workflow.
"""

import time
from typing import Dict, Optional

from app.core.config import Settings
from app.core.errors import DocumentProcessingError
from app.rag.graphs.query_graph import create_query_graph
from app.rag.graphs.query_state import QueryState


class QueryPipeline:
    """Query/retrieval pipeline."""

    def __init__(self, settings: Settings):
        """
        Initialize query pipeline.

        Args:
            settings (Settings): Application settings.
        """
        self.settings = settings
        self.graph = create_query_graph(settings)

    async def process_query(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[dict] = None,
        session_id: Optional[str] = None,
    ) -> Dict:
        """
        Process a query through the RAG pipeline.

        Args:
            query (str): User query text.
            top_k (Optional[int]): Number of chunks to retrieve.
            filter_metadata (Optional[dict]): Metadata filters for retrieval.
            session_id (Optional[str]): Session ID for conversation tracking.

        Returns:
            Dict: Query results including answer, chunks, and timing.

        Raises:
            DocumentProcessingError: If query processing fails.
        """
        # Initialize state with defaults
        initial_state: QueryState = {
            "query": query,
            "top_k": top_k or self.settings.query_top_k,
            "filter_metadata": filter_metadata,
            "session_id": session_id,
            "query_embedding": None,
            "retrieved_chunks": None,
            "context": None,
            "answer": None,
            "query_start_time": time.time(),
            "query_end_time": None,
            "errors": [],
            "status": "pending",
        }

        try:
            # Execute graph
            final_state = await self.graph.ainvoke(initial_state)

            # Check for errors
            if final_state["status"] == "failed":
                error_msg = "; ".join(final_state["errors"])
                raise DocumentProcessingError(
                    f"Query processing failed: {error_msg}",
                    details={
                        "query": query[:100],
                        "errors": final_state["errors"],
                    },
                )

            # Calculate query time
            query_time_ms = (
                final_state["query_end_time"] - final_state["query_start_time"]
            ) * 1000

            # Return results
            return {
                "answer": final_state["answer"],
                "retrieved_chunks": final_state["retrieved_chunks"] or [],
                "query_time_ms": query_time_ms,
                "status": final_state["status"],
            }

        except DocumentProcessingError:
            raise
        except Exception as e:
            raise DocumentProcessingError(
                f"Unexpected error processing query: {str(e)}",
                details={"query": query[:100], "error": str(e)},
            )
