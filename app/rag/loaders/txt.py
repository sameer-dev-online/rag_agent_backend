"""
Text file document loader with encoding detection.
"""

import hashlib
from pathlib import Path

import aiofiles

from app.core.errors import DocumentProcessingError
from app.models.document import Document, DocumentMetadata

from .base import BaseDocumentLoader


class TXTLoader(BaseDocumentLoader):
    """Text file document loader."""

    async def load(self) -> Document:
        """
        Load and parse text document.

        Returns:
            Document: Parsed text document.

        Raises:
            DocumentProcessingError: If text loading fails.
        """
        self._validate_file_exists()
        self._validate_file_readable()

        try:
            # Read file content
            content_bytes = self.file_path.read_bytes()
            file_hash = hashlib.sha256(content_bytes).hexdigest()
            file_size = len(content_bytes)

            # Try to decode with UTF-8 first, fallback to latin-1
            try:
                content = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                content = content_bytes.decode("latin-1")

            # Create metadata
            metadata = DocumentMetadata(
                filename=self.file_path.name,
                file_size_bytes=file_size,
                file_hash=file_hash,
                source_type="txt",
            )

            # Create document
            document = Document(content=content.strip(), metadata=metadata)

            return document

        except Exception as e:
            raise DocumentProcessingError(
                f"Failed to load text file: {self.file_path.name}",
                details={"filename": self.file_path.name, "error": str(e)},
            )
