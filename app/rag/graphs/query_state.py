"""
Query workflow state definition.
"""

from typing import List, Optional, TypedDict

from app.models.document import DocumentChunk


class QueryState(TypedDict):
    """
    State for query/retrieval workflow.

    Tracks the progression through:
    1. Query embedding generation
    2. Vector similarity search
    3. Context formatting
    4. Answer generation
    """

    # Input parameters
    query: str
    top_k: int
    filter_metadata: Optional[dict]
    session_id: Optional[str]

    # Processing stages
    query_embedding: Optional[List[float]]
    retrieved_chunks: Optional[List[DocumentChunk]]
    context: Optional[str]
    answer: Optional[str]

    # Timing and status tracking
    query_start_time: float
    query_end_time: Optional[float]
    errors: List[str]
    status: str  # pending, embedding_complete, retrieval_complete, formatting_complete, completed, failed
