"""
PDF document loader using PyMuPDF.
"""

import hashlib
from pathlib import Path

import fitz  # PyMuPDF

from app.core.errors import DocumentProcessingError
from app.models.document import Document, DocumentMetadata

from .base import BaseDocumentLoader


class PDFLoader(BaseDocumentLoader):
    """PDF document loader using PyMuPDF."""

    async def load(self) -> Document:
        """
        Load and parse PDF document.

        Returns:
            Document: Parsed PDF document.

        Raises:
            DocumentProcessingError: If PDF loading fails.
        """
        self._validate_file_exists()
        self._validate_file_readable()

        try:
            # Read file content for hash
            content_bytes = self.file_path.read_bytes()
            file_hash = hashlib.sha256(content_bytes).hexdigest()
            file_size = len(content_bytes)

            # Open PDF with PyMuPDF
            pdf_document = fitz.open(self.file_path)

            # Extract text from all pages
            text_content = []
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                text_content.append(page.get_text())

            # Combine all pages
            full_text = "\n\n".join(text_content)
            page_count = len(pdf_document)

            pdf_document.close()

            # Create metadata
            metadata = DocumentMetadata(
                filename=self.file_path.name,
                file_size_bytes=file_size,
                file_hash=file_hash,
                source_type="pdf",
                page_count=page_count,
            )

            # Create document
            document = Document(content=full_text.strip(), metadata=metadata)

            return document

        except fitz.FileDataError as e:
            raise DocumentProcessingError(
                f"Invalid PDF file: {self.file_path.name}",
                details={"filename": self.file_path.name, "error": str(e)},
            )
        except Exception as e:
            raise DocumentProcessingError(
                f"Failed to load PDF: {self.file_path.name}",
                details={"filename": self.file_path.name, "error": str(e)},
            )
