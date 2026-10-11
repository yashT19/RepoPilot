from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class ChangeRequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"
    FAILED = "FAILED"


class ChangeRequest(Base):

    __tablename__ = "change_requests"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    repository_id = Column(
        Integer,
        ForeignKey("repositories.id"),
        nullable=False,
        index=True
    )

    user_request = Column(
        Text,
        nullable=False
    )

    status = Column(
        SqlEnum(ChangeRequestStatus),
        nullable=False,
        default=ChangeRequestStatus.PENDING
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    repository = relationship(
        "Repository"
    )

    files = relationship(
        "ProposedFileChange",
        back_populates="change_request",
        cascade="all, delete-orphan"
    )