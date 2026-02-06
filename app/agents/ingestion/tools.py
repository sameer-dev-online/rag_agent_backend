"""
Tools for the ingestion agent.
"""

from pathlib import Path
from typing import Dict

from app.core.config import Settings
from app.core.constants import SUPPORTED_EXTENSIONS
from app.core.errors import FileValidationError, FileTooLargeError, UnsupportedFileTypeError
from app.rag.pipelines.ingestion import IngestionPipeline


async def validate_file_tool(file_path: str, settings: Settings) -> Dict:
    """
    Validate a file before processing.

    Args:
        file_path (str): Path to the file to validate.
        settings (Settings): Application settings.

    Returns:
        Dict: Validation result.
    """
    try:
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            return {
                "valid": False,
                "error": f"File not found: {file_path}",
            }

        # Check if it's a file
        if not path.is_file():
            return {
                "valid": False,
                "error": f"Not a file: {file_path}",
            }

        # Check file extension
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            supported = ", ".join(SUPPORTED_EXTENSIONS)
            return {
                "valid": False,
                "error": f"Unsupported file type: {path.suffix}. Supported: {supported}",
            }

        # Check file size
        file_size_bytes = path.stat().st_size
        if file_size_bytes > settings.max_file_size_bytes:
            size_mb = file_size_bytes / (1024 * 1024)
            return {
                "valid": False,
                "error": f"File too large: {size_mb:.2f}MB (max: {settings.max_file_size_mb}MB)",
            }

        # Validation passed
        return {
            "valid": True,
            "filename": path.name,
            "size_bytes": file_size_bytes,
            "file_type": path.suffix.lower().lstrip("."),
        }

    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}",
        }


async def process_document_tool(file_path: str, settings: Settings) -> Dict:
    """
    Process a document through the ingestion pipeline.

    Args:
        file_path (str): Path to the document file.
        settings (Settings): Application settings.

    Returns:
        Dict: Processing results.
    """
    try:
        # Create pipeline
        pipeline = IngestionPipeline(settings)

        # Process document
        result = await pipeline.process_document(Path(file_path))

        return {
            "success": True,
            **result,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "filename": Path(file_path).name,
        }
