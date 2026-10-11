from pydantic import BaseModel
from typing import Dict

class CodeDocument(BaseModel):
    file_path:str
    language:str
    content:str
    metadata:Dict={}