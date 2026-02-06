"""
Upload orchestration service.
"""

from typing import List

from fastapi import UploadFile

from app.agents.ingestion.agent import IngestionAgent
from app.core.config import Settings
from app.models.schemas import FileProcessingDetail, UploadResponse

from .file_service import FileService
from .validation_service import ValidationService


class UploadService:
    """Service for orchestrating file upload and processing."""

    def __init__(self, settings: Settings):
        """
        Initialize upload service.

        Args:
            settings (Settings): Application settings.
        """
        self.settings = settings
        self.validation_service = ValidationService(settings)
        self.file_service = FileService(settings)
        self.ingestion_agent = IngestionAgent(settings)

    async def process_upload(self, files: List[UploadFile]) -> UploadResponse:
        """
        Process uploaded files through the complete pipeline.

        Steps:
        1. Validate files
        2. Save files to temp directory
        3. Process files with ingestion agent
        4. Cleanup temp files
        5. Return results

        Args:
            files (List[UploadFile]): List of uploaded files.

        Returns:
            UploadResponse: Processing results.
        """
        saved_paths = []

        try:
            # Step 1: Validate files
            await self.validation_service.validate_files(files)

            # Step 2: Save files
            saved_paths = await self.file_service.save_upload_files(files)

            # Step 3: Process files with ingestion agent
            processing_results = await self.ingestion_agent.process_files(saved_paths)

            # Step 4: Build response
            details = []
            successful_count = 0
            total_chunks = 0

            for result in processing_results:
                detail = FileProcessingDetail(
                    filename=result["filename"],
                    file_size_bytes=result.get("file_size_bytes", 0),
                    chunks_created=result["chunks_created"],
                    processing_time_ms=result["processing_time_ms"],
                    status="success" if result["success"] else "failed",
                    error=result.get("error"),
                )
                details.append(detail)

                if result["success"]:
                    successful_count += 1
                    total_chunks += result["chunks_created"]

            # Create response
            response = UploadResponse(
                success=successful_count > 0,
                files_processed=successful_count,
                chunks_created=total_chunks,
                message=f"Successfully processed {successful_count}/{len(files)} files",
                details=details,
            )

            return response

        finally:
            # Step 5: Cleanup temp files (always execute)
            if saved_paths:
                self.file_service.cleanup_files(saved_paths)
