"""
PydanticAI ingestion agent for document processing.
"""

from pathlib import Path
from typing import Dict, List

from pydantic_ai import Agent

from app.core.config import Settings
from app.core.errors import DocumentProcessingError

from .prompts import INGESTION_AGENT_SYSTEM_PROMPT
from .tools import process_document_tool, validate_file_tool


class IngestionAgent:
    """PydanticAI agent for document ingestion."""

    def __init__(self, settings: Settings):
        """
        Initialize ingestion agent.

        Args:
            settings (Settings): Application settings.
        """
        self.settings = settings

        # Create PydanticAI agent
        self.agent = Agent(
            model="openai:gpt-4o-mini",
            system_prompt=INGESTION_AGENT_SYSTEM_PROMPT,
        )

    async def process_files(self, file_paths: List[Path]) -> List[Dict]:
        """
        Process multiple files through the ingestion pipeline.

        Args:
            file_paths (List[Path]): List of file paths to process.

        Returns:
            List[Dict]: Processing results for each file.
        """
        results = []

        for file_path in file_paths:
            result = await self._process_single_file(file_path)
            results.append(result)

        return results

    async def _process_single_file(self, file_path: Path) -> Dict:
        """
        Process a single file.

        Args:
            file_path (Path): Path to file.

        Returns:
            Dict: Processing result.
        """
        try:
            # Validate file
            validation_result = await validate_file_tool(str(file_path), self.settings)

            if not validation_result["valid"]:
                return {
                    "filename": file_path.name,
                    "success": False,
                    "error": validation_result["error"],
                    "chunks_created": 0,
                    "processing_time_ms": 0,
                }

            # Process document
            processing_result = await process_document_tool(str(file_path), self.settings)

            return {
                "filename": file_path.name,
                "success": processing_result["success"],
                "error": processing_result.get("error"),
                "chunks_created": processing_result.get("chunks_created", 0),
                "processing_time_ms": processing_result.get("processing_time_ms", 0),
                "file_size_bytes": validation_result["size_bytes"],
            }

        except Exception as e:
            return {
                "filename": file_path.name,
                "success": False,
                "error": str(e),
                "chunks_created": 0,
                "processing_time_ms": 0,
            }
