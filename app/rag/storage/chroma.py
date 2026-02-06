"""
ChromaDB local persistent vector store.
"""

from typing import Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import Settings
from app.core.errors import VectorStoreError
from app.models.document import DocumentChunk, DocumentMetadata

from .base import BaseVectorStore


class ChromaLocalVectorStore(BaseVectorStore):
    """ChromaDB local persistent vector store implementation."""

    def __init__(self, settings: Settings):
        """
        Initialize local ChromaDB vector store.

        Args:
            settings (Settings): Application settings.
        """
        self.settings = settings

        try:
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(
                path=str(settings.chroma_persist_dir),
                settings=ChromaSettings(anonymized_telemetry=False),
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={"description": "RAG document chunks"},
            )

        except Exception as e:
            raise VectorStoreError(
                f"Failed to initialize local ChromaDB: {str(e)}",
                details={"persist_dir": str(settings.chroma_persist_dir), "error": str(e)},
            )

    async def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        """
        Add document chunks to ChromaDB.

        Args:
            chunks (List[DocumentChunk]): Chunks with embeddings to store.

        Raises:
            VectorStoreError: If storing chunks fails.
        """
        if not chunks:
            return

        try:
            # Prepare data for ChromaDB
            ids = [str(chunk.id) for chunk in chunks]
            embeddings = [chunk.embedding for chunk in chunks]
            documents = [chunk.content for chunk in chunks]

            # Convert metadata to dict format
            metadatas = [
                {
                    "document_id": str(chunk.document_id),
                    "chunk_index": chunk.chunk_index,
                    "filename": chunk.metadata.filename,
                    "file_hash": chunk.metadata.file_hash,
                    "source_type": chunk.metadata.source_type,
                }
                for chunk in chunks
            ]

            # Add to collection
            self.collection.add(
                ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
            )

        except Exception as e:
            raise VectorStoreError(
                f"Failed to add chunks to local ChromaDB: {str(e)}",
                details={"chunk_count": len(chunks), "error": str(e)},
            )

    async def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 5,
        filter_metadata: Optional[Dict] = None,
    ) -> List[DocumentChunk]:
        """
        Search for similar chunks using embedding similarity.

        Args:
            query_embedding (List[float]): Query embedding vector.
            k (int): Number of results to return.
            filter_metadata (Optional[Dict]): Metadata filters.

        Returns:
            List[DocumentChunk]: Most similar chunks.

        Raises:
            VectorStoreError: If search fails.
        """
        try:
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding], n_results=k, where=filter_metadata
            )

            # Convert results to DocumentChunk objects
            chunks = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    metadata_dict = results["metadatas"][0][i]

                    # Reconstruct DocumentMetadata
                    metadata = DocumentMetadata(
                        filename=metadata_dict["filename"],
                        file_size_bytes=0,  # Not stored in ChromaDB
                        file_hash=metadata_dict["file_hash"],
                        source_type=metadata_dict["source_type"],
                    )

                    # Create DocumentChunk
                    chunk = DocumentChunk(
                        id=results["ids"][0][i],
                        document_id=metadata_dict["document_id"],
                        content=results["documents"][0][i],
                        chunk_index=metadata_dict["chunk_index"],
                        metadata=metadata,
                        embedding=results["embeddings"][0][i] if results["embeddings"] else None,
                    )
                    chunks.append(chunk)

            return chunks

        except Exception as e:
            raise VectorStoreError(
                f"Failed to search local ChromaDB: {str(e)}",
                details={"k": k, "error": str(e)},
            )

    async def delete_by_document_id(self, document_id: str) -> None:
        """
        Delete all chunks for a specific document.

        Args:
            document_id (str): Document ID to delete.

        Raises:
            VectorStoreError: If deletion fails.
        """
        try:
            self.collection.delete(where={"document_id": document_id})

        except Exception as e:
            raise VectorStoreError(
                f"Failed to delete document from local ChromaDB: {str(e)}",
                details={"document_id": document_id, "error": str(e)},
            )

    async def count(self) -> int:
        """
        Get total number of chunks in the store.

        Returns:
            int: Number of chunks.
        """
        try:
            return self.collection.count()

        except Exception as e:
            raise VectorStoreError(
                f"Failed to count chunks in local ChromaDB: {str(e)}",
                details={"error": str(e)},
            )
