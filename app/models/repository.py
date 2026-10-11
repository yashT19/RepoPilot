from datetime import datetime
from enum import Enum
from sqlalchemy import Column, DateTime,Enum as SqlEnum, Integer, String
from app.database.database import Base

class RepositoryStatus(str,Enum):
    UPLOADED = "UPLOADED"
    PARSED = "PARSED"
    INDEXED = "INDEXED"

class Repository(Base):
    __tablename__="repositories"
    id=Column(Integer, primary_key=True, index=True)   
    name=Column(String(255), nullable=False) 
    storage_path = Column(String(500), nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    status = Column(
        SqlEnum(RepositoryStatus),
        default=RepositoryStatus.UPLOADED,
        nullable=False
    )