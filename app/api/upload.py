"""
Upload endpoint for document ingestion.
"""

from typing import List

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.dependencies import get_upload_service
from app.models.schemas import UploadResponse
from app.services.upload_service import UploadService

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_documents(
    files: List[UploadFile] = File(..., description="Document files to upload and process"),
    upload_service: UploadService = Depends(get_upload_service),
) -> UploadResponse:
    """
    Upload and process documents for RAG system.

    Accepts multiple files (PDF, TXT, DOCX) and processes them through:
    1. Validation (file type, size)
    2. Loading (parse document content)
    3. Chunking (split into appropriately sized pieces)
    4. Embedding (generate vector embeddings)
    5. Storage (store in vector database)

    Files are temporarily saved, processed, and immediately deleted.
    The content is preserved in the vector store.

    Args:
        files (List[UploadFile]): Document files to process.
        upload_service (UploadService): Injected upload service.

    Returns:
        UploadResponse: Processing results including chunks created and status.

    Raises:
        400: File validation failed
        413: File too large
        500: Processing error
    """
    result = await upload_service.process_upload(files)
    return result
