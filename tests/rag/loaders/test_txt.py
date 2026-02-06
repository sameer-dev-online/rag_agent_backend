"""
Tests for text file loader.
"""

import pytest
from pathlib import Path

from app.core.errors import DocumentProcessingError
from app.rag.loaders.txt import TXTLoader


@pytest.mark.asyncio
async def test_txt_loader_success(sample_txt_path: Path):
    """
    Test successful text file loading.

    Args:
        sample_txt_path (Path): Path to sample text file.
    """
    loader = TXTLoader(sample_txt_path)
    document = await loader.load()

    assert document is not None
    assert document.content == "Sample text content for testing."
    assert document.metadata.filename == "test.txt"
    assert document.metadata.source_type == "txt"
    assert document.metadata.file_size_bytes > 0
    assert len(document.metadata.file_hash) == 64  # SHA-256 hex


@pytest.mark.asyncio
async def test_txt_loader_empty_file(tmp_path: Path):
    """
    Test loading empty text file.

    Args:
        tmp_path (Path): Pytest temporary directory.
    """
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")

    loader = TXTLoader(empty_file)
    document = await loader.load()

    assert document is not None
    assert document.content == ""
    assert document.metadata.file_size_bytes == 0


@pytest.mark.asyncio
async def test_txt_loader_file_not_found():
    """Test loading non-existent file."""
    loader = TXTLoader(Path("/nonexistent/file.txt"))

    with pytest.raises(FileNotFoundError):
        await loader.load()


@pytest.mark.asyncio
async def test_txt_loader_large_file(tmp_path: Path):
    """
    Test loading large text file.

    Args:
        tmp_path (Path): Pytest temporary directory.
    """
    large_file = tmp_path / "large.txt"
    content = "A" * 10000  # 10KB of text
    large_file.write_text(content)

    loader = TXTLoader(large_file)
    document = await loader.load()

    assert document is not None
    assert len(document.content) == 10000
    assert document.metadata.file_size_bytes == 10000
