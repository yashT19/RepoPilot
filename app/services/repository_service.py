from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.repository import Repository, RepositoryStatus
from app.repository_processing.storage_service import StorageService
from app.schemas.repository import RepositoryUploadResponse
from app.services.repository_processing_service import (
RepositoryProcessingService
)

class RepositoryService:

   def __init__(
    self,
    storage_service: StorageService,
    db: Session,
    processing_service: RepositoryProcessingService
):
    self.storage_service = storage_service
    self.db = db
    self.processing_service = processing_service

   def upload_repository(
    self,
    uploaded_file: UploadFile
) -> RepositoryUploadResponse:

    # --------------------------------------------------
    # 1. Create repository directory
    # --------------------------------------------------

    repository_path = (
        self.storage_service.create_repository_directory()
    )

    # --------------------------------------------------
    # 2. Save uploaded ZIP
    # --------------------------------------------------

    zip_path = self.storage_service.save_zip(
        uploaded_file,
        repository_path
    )

    # --------------------------------------------------
    # 3. Extract repository
    # --------------------------------------------------

    self.storage_service.extract_zip(
        zip_path,
        repository_path
    )

    # --------------------------------------------------
    # 4. Create repository record
    #
    # We create the DB record BEFORE processing because
    # the repository ID is required for repository-specific
    # vector storage.
    # --------------------------------------------------

    repository = Repository(
        name=Path(uploaded_file.filename).stem,
        storage_path=str(repository_path),
        status=RepositoryStatus.UPLOADED
    )

    self.db.add(repository)
    self.db.commit()
    self.db.refresh(repository)

    # At this point we have:
    #
    # repository.id
    #
    # Example:
    #
    # repository.id = 2

    # --------------------------------------------------
    # 5. Process repository
    #
    # Parser
    #    ↓
    # Documents
    #    ↓
    # Chunker
    #    ↓
    # Chunks
    #    ↓
    # Embeddings
    #    ↓
    # Repository-specific FAISS
    #    ↓
    # Persist FAISS
    # --------------------------------------------------

    extracted_path = repository_path / "extracted"

    processing_result = (
        self.processing_service.process_repository(
            repository_path=extracted_path,
            repository_id=repository.id
        )
    )

    # --------------------------------------------------
    # 6. Return API response
    # --------------------------------------------------

    return RepositoryUploadResponse(
        repository_id=repository.id,
        repository_name=repository.name,
        status=repository.status.value,
        message=(
            f"Repository uploaded and processed successfully. "
            f"Documents: {processing_result['documents']}, "
            f"Chunks: {processing_result['chunks']}"
        )
    )