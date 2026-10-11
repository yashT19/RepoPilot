from pathlib import Path
from uuid import uuid4
import shutil
import zipfile
from app.config.settings import settings
from fastapi import UploadFile

class StorageService:
    def __init__(self):
        self.storage_root=Path(settings.STORAGE_ROOT)
        self.storage_root.mkdir(parents=True, exist_ok=True)

    def create_repository_directory(self)-> Path:
        repository_id= str(uuid4())
        repository_path=self.storage_root/repository_id
        repository_path.mkdir(parents=True)
        return repository_path    
    def save_zip(self,
                 uploaded_file:UploadFile,
                 repository_path:Path)-> Path:
        zip_path = repository_path / "original.zip"
        with zip_path.open("wb") as buffer:
             shutil.copyfileobj(uploaded_file.file, buffer)
        return zip_path     


    def extract_zip(self, 
                    zip_path:Path,
                    repository_path:Path)-> Path:
        extracted_path = repository_path / "extracted"
        extracted_path.mkdir(exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extracted_path)
        return extracted_path    
