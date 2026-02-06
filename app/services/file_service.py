"""
File handling service.
"""

import aiofiles
from pathlib import Path
from typing import List

from fastapi import UploadFile

from app.core.config import Settings
from app.utils.file_utils import cleanup_files, ensure_directory_exists, generate_unique_filename
from app.utils.hash_utils import calculate_file_hash


class FileService:
    """Service for file operations."""

    def __init__(self, settings: Settings):
        """
        Initialize file service.

        Args:
            settings (Settings): Application settings.
        """
        self.settings = settings
        ensure_directory_exists(settings.upload_dir)

    async def save_upload_files(self, files: List[UploadFile]) -> List[Path]:
        """
        Save uploaded files to temporary directory.

        Args:
            files (List[UploadFile]): List of uploaded files.

        Returns:
            List[Path]: List of saved file paths.
        """
        saved_paths = []

        for file in files:
            # Generate unique filename
            unique_filename = generate_unique_filename(file.filename)
            file_path = self.settings.upload_dir / unique_filename

            # Save file
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)

            saved_paths.append(file_path)

        return saved_paths

    def cleanup_files(self, file_paths: List[Path]) -> None:
        """
        Delete temporary files.

        Args:
            file_paths (List[Path]): List of file paths to delete.
        """
        cleanup_files(file_paths)

    def calculate_hash(self, file_path: Path) -> str:
        """
        Calculate SHA-256 hash of a file.

        Args:
            file_path (Path): Path to the file.

        Returns:
            str: SHA-256 hash hexdigest.
        """
        return calculate_file_hash(file_path)
