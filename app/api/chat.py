"""
Chat endpoint for RAG query/retrieval.
"""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_query_service
from app.models.schemas import ChatRequest, ChatResponse
from app.services.query_service import QueryService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    query_service: QueryService = Depends(get_query_service),
) -> ChatResponse:
    """
    Chat endpoint for RAG query/retrieval.

    Process user queries against the document knowledge base:
    1. Generate query embedding
    2. Retrieve relevant chunks from vector database
    3. Format context with source attribution
    4. Generate grounded answer using LLM
    5. Return answer with sources

    The system generates answers based ONLY on retrieved context to ensure
    grounded, factual responses without hallucination.

    Args:
        request (ChatRequest): Chat request containing query and parameters.
        query_service (QueryService): Injected query service.

    Returns:
        ChatResponse: Answer with sources, retrieved chunks, and timing.

    Raises:
        422: Invalid request parameters
        500: Query processing error
    """
    result = await query_service.process_chat_query(request)
    return result
