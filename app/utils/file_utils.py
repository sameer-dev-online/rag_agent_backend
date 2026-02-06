"""
File operation utilities.
"""

import uuid
from pathlib import Path
from typing import List


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename while preserving extension.

    Args:
        original_filename (str): Original filename.

    Returns:
        str: Unique filename.
    """
    path = Path(original_filename)
    extension = path.suffix
    unique_name = f"{uuid.uuid4().hex}{extension}"
    return unique_name


def ensure_directory_exists(directory: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory (Path): Directory path.
    """
    directory.mkdir(parents=True, exist_ok=True)


def cleanup_files(file_paths: List[Path]) -> None:
    """
    Delete files from filesystem.

    Args:
        file_paths (List[Path]): List of file paths to delete.
    """
    for file_path in file_paths:
        try:
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
        except Exception:
            # Ignore errors during cleanup
            pass
