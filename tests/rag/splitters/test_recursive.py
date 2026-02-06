"""
Tests for recursive text splitter.
"""

import pytest

from app.rag.splitters.config import SplitterConfig
from app.rag.splitters.recursive import RecursiveTextSplitter


@pytest.mark.asyncio
async def test_recursive_splitter_basic(sample_document):
    """
    Test basic text splitting.

    Args:
        sample_document: Sample document fixture.
    """
    config = SplitterConfig(chunk_size=20, chunk_overlap=5)
    splitter = RecursiveTextSplitter(config)

    chunks = await splitter.split(sample_document)

    assert len(chunks) > 0
    for chunk in chunks:
        assert len(chunk.content) <= 25  # Allow for overlap
        assert chunk.document_id == sample_document.id
        assert chunk.metadata == sample_document.metadata


@pytest.mark.asyncio
async def test_recursive_splitter_no_overlap(sample_document):
    """
    Test splitting without overlap.

    Args:
        sample_document: Sample document fixture.
    """
    config = SplitterConfig(chunk_size=20, chunk_overlap=0)
    splitter = RecursiveTextSplitter(config)

    chunks = await splitter.split(sample_document)

    assert len(chunks) > 0
    for chunk in chunks:
        assert len(chunk.content) <= 20


@pytest.mark.asyncio
async def test_recursive_splitter_chunk_indices(sample_document):
    """
    Test that chunk indices are sequential.

    Args:
        sample_document: Sample document fixture.
    """
    config = SplitterConfig(chunk_size=20, chunk_overlap=5)
    splitter = RecursiveTextSplitter(config)

    chunks = await splitter.split(sample_document)

    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i


@pytest.mark.asyncio
async def test_recursive_splitter_invalid_config():
    """Test splitter with invalid configuration."""
    with pytest.raises(ValueError):
        config = SplitterConfig(chunk_size=100, chunk_overlap=150)
        config.validate_config()
