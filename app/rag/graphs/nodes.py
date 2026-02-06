"""
LangGraph workflow nodes for document ingestion.
"""

import time
from pathlib import Path
from typing import Dict

from app.core.errors import DocumentProcessingError
from app.rag.embeddings.base import BaseEmbedder
from app.rag.loaders.factory import DocumentLoaderFactory
from app.rag.splitters.base import BaseTextSplitter
from app.rag.storage.base import BaseVectorStore

from .state import IngestionState


async def load_document_node(state: IngestionState) -> Dict:
    """
    Load document from file path.

    Args:
        state (IngestionState): Current workflow state.

    Returns:
        Dict: Updated state with document.
    """
    try:
        file_path = Path(state["file_path"])

        # Create appropriate loader
        loader = DocumentLoaderFactory.create_loader(file_path)

        # Load document
        document = await loader.load()

        return {
            "document": document,
            "status": "loading_complete",
        }

    except Exception as e:
        return {
            "errors": state["errors"] + [f"Loading failed: {str(e)}"],
            "status": "failed",
        }


async def split_document_node(
    state: IngestionState, splitter: BaseTextSplitter
) -> Dict:
    """
    Split document into chunks.

    Args:
        state (IngestionState): Current workflow state.
        splitter (BaseTextSplitter): Text splitter instance.

    Returns:
        Dict: Updated state with chunks.
    """
    try:
        if not state["document"]:
            raise DocumentProcessingError("No document to split")

        # Split document
        
        chunks = await splitter.split(state["document"])

        return {
            "chunks": chunks,
            "status": "splitting_complete",
        }

    except Exception as e:
        return {
            "errors": state["errors"] + [f"Splitting failed: {str(e)}"],
            "status": "failed",
        }


async def embed_chunks_node(
    state: IngestionState, embedder: BaseEmbedder
) -> Dict:
    """
    Generate embeddings for chunks.

    Args:
        state (IngestionState): Current workflow state.
        embedder (BaseEmbedder): Embedder instance.

    Returns:
        Dict: Updated state with embedded chunks.
    """
    try:
        if not state["chunks"]:
            raise DocumentProcessingError("No chunks to embed")

        # Generate embeddings
        embedded_chunks = await embedder.embed_chunks(state["chunks"])

        return {
            "embedded_chunks": embedded_chunks,
            "status": "embedding_complete",
        }

    except Exception as e:
        return {
            "errors": state["errors"] + [f"Embedding failed: {str(e)}"],
            "status": "failed",
        }


async def store_chunks_node(
    state: IngestionState, vector_store: BaseVectorStore
) -> Dict:
    """
    Store chunks in vector store.

    Args:
        state (IngestionState): Current workflow state.
        vector_store (BaseVectorStore): Vector store instance.

    Returns:
        Dict: Updated state with completion status.
    """
    try:
        if not state["embedded_chunks"]:
            raise DocumentProcessingError("No embedded chunks to store")

        # Store chunks
        await vector_store.add_chunks(state["embedded_chunks"])

        return {
            "processing_end_time": time.time(),
            "status": "completed",
        }

    except Exception as e:
        return {
            "errors": state["errors"] + [f"Storage failed: {str(e)}"],
            "processing_end_time": time.time(),
            "status": "failed",
        }
