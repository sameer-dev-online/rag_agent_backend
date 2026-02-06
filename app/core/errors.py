"""
Custom exception hierarchy for the RAG application.
"""

from typing import Any, Dict, Optional


class RAGException(Exception):
    """Base exception for all RAG-related errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
    ):
        """
        Initialize RAG exception.

        Args:
            message (str): Error message.
            details (Optional[Dict[str, Any]]): Additional error details.
            status_code (int): HTTP status code.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.status_code = status_code


class FileValidationError(RAGException):
    """Raised when file validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize file validation error.

        Args:
            message (str): Error message.
            details (Optional[Dict[str, Any]]): Additional error details.
        """
        super().__init__(message, details, status_code=400)


class FileTooLargeError(RAGException):
    """Raised when uploaded file exceeds size limit."""

    def __init__(self, filename: str, size_mb: float, max_mb: float):
        """
        Initialize file too large error.

        Args:
            filename (str): Name of the file.
            size_mb (float): Actual file size in MB.
            max_mb (float): Maximum allowed size in MB.
        """
        message = f"File '{filename}' ({size_mb:.2f}MB) exceeds maximum size ({max_mb}MB)"
        details = {"filename": filename, "size_mb": size_mb, "max_mb": max_mb}
        super().__init__(message, details, status_code=413)


class UnsupportedFileTypeError(RAGException):
    """Raised when file type is not supported."""

    def __init__(self, filename: str, file_type: str, supported_types: list):
        """
        Initialize unsupported file type error.

        Args:
            filename (str): Name of the file.
            file_type (str): Actual file type.
            supported_types (list): List of supported file types.
        """
        message = f"File '{filename}' has unsupported type '{file_type}'. Supported types: {', '.join(supported_types)}"
        details = {
            "filename": filename,
            "file_type": file_type,
            "supported_types": supported_types,
        }
        super().__init__(message, details, status_code=400)


class TooManyFilesError(RAGException):
    """Raised when too many files are uploaded at once."""

    def __init__(self, file_count: int, max_files: int):
        """
        Initialize too many files error.

        Args:
            file_count (int): Number of files uploaded.
            max_files (int): Maximum allowed files.
        """
        message = f"Too many files uploaded ({file_count}). Maximum allowed: {max_files}"
        details = {"file_count": file_count, "max_files": max_files}
        super().__init__(message, details, status_code=400)


class DocumentProcessingError(RAGException):
    """Raised when document processing fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize document processing error.

        Args:
            message (str): Error message.
            details (Optional[Dict[str, Any]]): Additional error details.
        """
        super().__init__(message, details, status_code=500)


class EmbeddingError(RAGException):
    """Raised when embedding generation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize embedding error.

        Args:
            message (str): Error message.
            details (Optional[Dict[str, Any]]): Additional error details.
        """
        super().__init__(message, details, status_code=500)


class VectorStoreError(RAGException):
    """Raised when vector store operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize vector store error.

        Args:
            message (str): Error message.
            details (Optional[Dict[str, Any]]): Additional error details.
        """
        super().__init__(message, details, status_code=500)


class ConfigurationError(RAGException):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration error.

        Args:
            message (str): Error message.
            details (Optional[Dict[str, Any]]): Additional error details.
        """
        super().__init__(message, details, status_code=500)
