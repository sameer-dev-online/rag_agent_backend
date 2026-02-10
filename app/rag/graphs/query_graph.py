"""
LangGraph workflow builder for query/retrieval.
"""

import os

from langgraph.graph import END, StateGraph
from openai import AsyncOpenAI

from app.core.config import Settings
from app.rag.embeddings.factory import EmbedderFactory
from app.rag.storage.factory import VectorStoreFactory

from .query_nodes import (
    embed_query_node,
    format_context_node,
    generate_answer_node,
    retrieve_chunks_node,
)
from .query_state import QueryState


def create_query_graph(settings: Settings) -> StateGraph:
    """
    Create LangGraph workflow for query/retrieval.

    Args:
        settings (Settings): Application settings.

    Returns:
        StateGraph: Compiled query graph.
    """
    # Initialize components
    embedder = EmbedderFactory.create_embedder(settings)
    vector_store = VectorStoreFactory.create_vector_store(settings)
    llm_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    

    # Create state graph
    workflow = StateGraph(QueryState)

    # Add nodes with dependency injection
    # Reason: Define async wrapper functions to properly await coroutines
    async def embed_with_embedder(state):
        return await embed_query_node(state, embedder)

    async def retrieve_with_store(state):
        return await retrieve_chunks_node(state, vector_store)

    async def format_with_config(state):
        return await format_context_node(state, settings.query_max_context_length)

    async def generate_with_llm(state):
        return await generate_answer_node(
            state, llm_client, settings.query_llm_model, settings.query_temperature
        )

    workflow.add_node("embed_query", embed_with_embedder)
    workflow.add_node("retrieve_chunks", retrieve_with_store)
    workflow.add_node("format_context", format_with_config)
    workflow.add_node("generate_answer", generate_with_llm)

    # Define edges (linear workflow sequence)
    workflow.set_entry_point("embed_query")
    workflow.add_edge("embed_query", "retrieve_chunks")
    workflow.add_edge("retrieve_chunks", "format_context")
    workflow.add_edge("format_context", "generate_answer")
    workflow.add_edge("generate_answer", END)

    # Compile graph
    compiled_graph = workflow.compile()

    return compiled_graph
