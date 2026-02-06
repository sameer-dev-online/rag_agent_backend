"""
Base document loader interface.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from app.models.document import Document


class BaseDocumentLoader(ABC):
    """Abstract base class for document loaders."""

    def __init__(self, file_path: Path):
        """
        Initialize document loader.

        Args:
            file_path (Path): Path to the document file.
        """
        self.file_path = file_path

    @abstractmethod
    async def load(self) -> Document:
        """
        Load and parse the document.

        Returns:
            Document: Parsed document with content and metadata.

        Raises:
            DocumentProcessingError: If document loading fails.
        """
        pass

    def _validate_file_exists(self) -> None:
        """
        Validate that the file exists.

        Raises:
            FileNotFoundError: If file doesn't exist.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

    def _validate_file_readable(self) -> None:
        """
        Validate that the file is readable.

        Raises:
            PermissionError: If file is not readable.
        """
        if not self.file_path.is_file():
            raise PermissionError(f"Not a file: {self.file_path}")
