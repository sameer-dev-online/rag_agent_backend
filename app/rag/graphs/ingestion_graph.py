"""
LangGraph workflow builder for document ingestion.
"""

from langgraph.graph import StateGraph, END

from app.core.config import Settings
from app.rag.embeddings.factory import EmbedderFactory
from app.rag.splitters.config import SplitterConfig
from app.rag.splitters.recursive import RecursiveTextSplitter
from app.rag.storage.factory import VectorStoreFactory

from .nodes import (
    embed_chunks_node,
    load_document_node,
    split_document_node,
    store_chunks_node,
)
from .state import IngestionState


def create_ingestion_graph(settings: Settings) -> StateGraph:
    """
    Create LangGraph workflow for document ingestion.

    Args:
        settings (Settings): Application settings.

    Returns:
        StateGraph: Compiled ingestion graph.
    """
    # Initialize components
    splitter_config = SplitterConfig(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    splitter = RecursiveTextSplitter(splitter_config)
    embedder = EmbedderFactory.create_embedder(settings)
    vector_store = VectorStoreFactory.create_vector_store(settings)

    # Create state graph
    workflow = StateGraph(IngestionState)

    # Add nodes with dependency injection
    # Reason: Define async wrapper functions instead of lambdas to properly await coroutines
    async def split_with_config(state):
        return await split_document_node(state, splitter)

    async def embed_with_config(state):
        return await embed_chunks_node(state, embedder)

    async def store_with_config(state):
        return await store_chunks_node(state, vector_store)

    workflow.add_node("load_document", load_document_node)
    workflow.add_node("split_document", split_with_config)
    workflow.add_node("embed_chunks", embed_with_config)
    workflow.add_node("store_chunks", store_with_config)

    # Define edges (workflow sequence)
    workflow.set_entry_point("load_document")
    workflow.add_edge("load_document", "split_document")
    workflow.add_edge("split_document", "embed_chunks")
    workflow.add_edge("embed_chunks", "store_chunks")
    workflow.add_edge("store_chunks", END)

    # Compile graph
    compiled_graph = workflow.compile()

    return compiled_graph
