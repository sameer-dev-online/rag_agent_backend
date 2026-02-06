"""
Document loader factory.
"""

from pathlib import Path
from typing import Dict, Type

from app.core.constants import FileType
from app.core.errors import UnsupportedFileTypeError

from .base import BaseDocumentLoader
from .docx import DOCXLoader
from .pdf import PDFLoader
from .txt import TXTLoader


class DocumentLoaderFactory:
    """Factory for creating document loaders based on file type."""

    _loaders: Dict[FileType, Type[BaseDocumentLoader]] = {
        FileType.PDF: PDFLoader,
        FileType.TXT: TXTLoader,
        FileType.DOCX: DOCXLoader,
    }

    @classmethod
    def create_loader(cls, file_path: Path) -> BaseDocumentLoader:
        """
        Create appropriate document loader based on file extension.

        Args:
            file_path (Path): Path to the document file.

        Returns:
            BaseDocumentLoader: Document loader instance.

        Raises:
            UnsupportedFileTypeError: If file type is not supported.
        """
        # Get file extension
        extension = file_path.suffix.lower().lstrip(".")

        # Map extension to FileType
        try:
            file_type = FileType(extension)
        except ValueError:
            supported = [ft.value for ft in FileType]
            raise UnsupportedFileTypeError(
                filename=file_path.name,
                file_type=extension,
                supported_types=supported,
            )

        # Get loader class
        loader_class = cls._loaders.get(file_type)
        if not loader_class:
            supported = [ft.value for ft in FileType]
            raise UnsupportedFileTypeError(
                filename=file_path.name,
                file_type=extension,
                supported_types=supported,
            )

        return loader_class(file_path)

    @classmethod
    def register_loader(cls, file_type: FileType, loader_class: Type[BaseDocumentLoader]) -> None:
        """
        Register a custom document loader.

        Args:
            file_type (FileType): File type enum.
            loader_class (Type[BaseDocumentLoader]): Loader class.
        """
        cls._loaders[file_type] = loader_class
