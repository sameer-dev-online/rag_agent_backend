"""
Query service for orchestrating chat query processing.
"""

from typing import List

from app.agents.query.agent import QueryAgent
from app.core.config import Settings
from app.core.logging import get_logger
from app.models.schemas import ChatRequest, ChatResponse, RetrievedChunk

logger = get_logger(__name__)


class QueryService:
    """
    Service for handling chat queries and building responses.

    This service orchestrates the query agent and formats results into API responses.
    """

    def __init__(self, settings: Settings):
        """
        Initialize query service.

        Args:
            settings (Settings): Application settings.
        """
        self.settings = settings
        self.query_agent = QueryAgent(settings)

    async def process_chat_query(self, request: ChatRequest) -> ChatResponse:
        """
        Process chat query and build response.

        Args:
            request (ChatRequest): Chat request containing query and parameters.

        Returns:
            ChatResponse: Complete chat response with answer, sources, and chunks.
        """
        try:
            logger.info(f"Processing chat query: {request.query[:100]}")

            # Process through agent
            result = await self.query_agent.process_query(
                query=request.query,
                top_k=request.top_k,
                filter_metadata=request.filter_metadata,
                session_id=request.session_id,
            )

            # Extract unique sources and format chunks
            sources: List[str] = []
            retrieved_chunks_data: List[RetrievedChunk] = []

            if result.get("retrieved_chunks"):
                seen_files = set()

                for chunk in result["retrieved_chunks"]:
                    # Extract source filename
                    filename = chunk.metadata.filename
                    if filename not in seen_files:
                        sources.append(filename)
                        seen_files.add(filename)

                    # Convert to API schema
                    retrieved_chunks_data.append(
                        RetrievedChunk(
                            chunk_id=str(chunk.id),
                            document_id=str(chunk.document_id),
                            content=chunk.content,
                            chunk_index=chunk.chunk_index,
                            filename=chunk.metadata.filename,
                            source_type=chunk.metadata.source_type,
                            similarity_score=None,  # Not included in current retrieval
                        )
                    )

            # Build response
            response = ChatResponse(
                success=result.get("success", False),
                answer=result.get("answer", "No answer generated."),
                sources=sources,
                retrieved_chunks=retrieved_chunks_data,
                query_time_ms=result.get("query_time_ms", 0),
                session_id=request.session_id,
                error=result.get("error"),
            )

            logger.info(
                f"Chat query completed: success={response.success}, "
                f"sources={len(sources)}, chunks={len(retrieved_chunks_data)}"
            )

            return response

        except Exception as e:
            logger.error(f"Error processing chat query: {e}")

            # Always return valid ChatResponse
            return ChatResponse(
                success=False,
                answer="Error processing query. Please try again.",
                sources=[],
                retrieved_chunks=[],
                query_time_ms=0,
                session_id=request.session_id,
                error=str(e),
            )
