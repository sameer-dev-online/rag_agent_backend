"""
Document ingestion pipeline wrapping LangGraph workflow.
"""

import time
from pathlib import Path
from typing import Dict

from app.core.config import Settings
from app.core.errors import DocumentProcessingError
from app.rag.graphs.ingestion_graph import create_ingestion_graph
from app.rag.graphs.state import IngestionState


class IngestionPipeline:
    """Document ingestion pipeline."""

    def __init__(self, settings: Settings):
        """
        Initialize ingestion pipeline.

        Args:
            settings (Settings): Application settings.
        """
        self.settings = settings
        self.graph = create_ingestion_graph(settings)

    async def process_document(self, file_path: Path) -> Dict:
        """
        Process a single document through the ingestion pipeline.

        Args:
            file_path (Path): Path to document file.

        Returns:
            Dict: Processing results including chunks created and status.

        Raises:
            DocumentProcessingError: If processing fails.
        """
        # Initialize state
        initial_state: IngestionState = {
            "file_path": str(file_path),
            "document": None,
            "chunks": None,
            "embedded_chunks": None,
            "processing_start_time": time.time(),
            "processing_end_time": None,
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
                    f"Document processing failed: {error_msg}",
                    details={
                        "filename": file_path.name,
                        "errors": final_state["errors"],
                    },
                )

            # Calculate processing time
            processing_time_ms = (
                final_state["processing_end_time"] - final_state["processing_start_time"]
            ) * 1000

            # Return results
            return {
                "filename": file_path.name,
                "chunks_created": len(final_state["embedded_chunks"]) if final_state["embedded_chunks"] else 0,
                "processing_time_ms": processing_time_ms,
                "status": final_state["status"],
                "document_id": str(final_state["document"].id) if final_state["document"] else None,
            }

        except DocumentProcessingError:
            raise
        except Exception as e:
            raise DocumentProcessingError(
                f"Unexpected error processing document: {str(e)}",
                details={"filename": file_path.name, "error": str(e)},
            )
