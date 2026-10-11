from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.container import container
from app.database.database import get_db
from app.repository_processing.storage_service import StorageService
from app.schemas.repository import RepositoryUploadResponse
from app.services.repository_service import RepositoryService


router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"]
)


@router.post(
    "/upload",
    response_model=RepositoryUploadResponse
)
def upload_repository(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are supported."
        )

    storage_service = StorageService()

    repository_service = RepositoryService(
        storage_service=storage_service,
        db=db,
        processing_service=container.processing_service
    )

    return repository_service.upload_repository(file)