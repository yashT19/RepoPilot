from pydantic import BaseModel

class RepositoryUploadResponse(BaseModel):
    repository_id:int
    repository_name:str
    status:str
    message:str
