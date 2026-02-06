"""
Recursive text splitter wrapping LangChain implementation.
"""

from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.models.document import Document, DocumentChunk

from .base import BaseTextSplitter
from .config import SplitterConfig


class RecursiveTextSplitter(BaseTextSplitter):
    """
    Recursive text splitter that splits on separators hierarchically.

    This wraps LangChain's RecursiveCharacterTextSplitter.
    """

    def __init__(self, config: SplitterConfig):
        """
        Initialize recursive text splitter.

        Args:
            config (SplitterConfig): Splitter configuration.
        """
        config.validate_config()
        self.config = config

        # Create LangChain splitter
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            keep_separator=config.keep_separator,
            length_function=len,
        )

    async def split(self, document: Document) -> List[DocumentChunk]:
        """
        Split document into chunks using recursive splitting.

        Args:
            document (Document): Document to split.

        Returns:
            List[DocumentChunk]: List of document chunks.
        """
        # Split text using LangChain splitter
        text_chunks = self._splitter.split_text(document.content)

        # Create DocumentChunk objects
        chunks = self._create_chunks(document, text_chunks)

        return chunks
