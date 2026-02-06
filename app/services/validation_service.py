"""
File validation service.
"""

from pathlib import Path
from typing import List

from fastapi import UploadFile

from app.core.config import Settings
from app.core.constants import MIME_TYPE_MAPPING, SUPPORTED_EXTENSIONS
from app.core.errors import (
    FileTooLargeError,
    TooManyFilesError,
    UnsupportedFileTypeError,
)


class ValidationService:
    """Service for validating uploaded files."""

    def __init__(self, settings: Settings):
        """
        Initialize validation service.

        Args:
            settings (Settings): Application settings.
        """
        self.settings = settings

    async def validate_files(self, files: List[UploadFile]) -> None:
        """
        Validate uploaded files.

        Args:
            files (List[UploadFile]): List of uploaded files.

        Raises:
            TooManyFilesError: If too many files uploaded.
            UnsupportedFileTypeError: If file type not supported.
            FileTooLargeError: If file exceeds size limit.
        """
        # Check file count
        if len(files) > self.settings.max_files_per_request:
            raise TooManyFilesError(len(files), self.settings.max_files_per_request)

        # Validate each file
        for file in files:
            await self._validate_single_file(file)

    async def _validate_single_file(self, file: UploadFile) -> None:
        """
        Validate a single uploaded file.

        Args:
            file (UploadFile): Uploaded file.

        Raises:
            UnsupportedFileTypeError: If file type not supported.
            FileTooLargeError: If file exceeds size limit.
        """
        # Check file extension
        file_path = Path(file.filename)
        extension = file_path.suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            supported = [ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS]
            raise UnsupportedFileTypeError(
                filename=file.filename,
                file_type=extension.lstrip("."),
                supported_types=supported,
            )

        # Check file size
        # Read file to get size
        content = await file.read()
        file_size_bytes = len(content)

        # Reset file pointer
        await file.seek(0)

        if file_size_bytes > self.settings.max_file_size_bytes:
            size_mb = file_size_bytes / (1024 * 1024)
            raise FileTooLargeError(
                filename=file.filename,
                size_mb=size_mb,
                max_mb=self.settings.max_file_size_mb,
            )
