from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class ProposedFileChange(Base):

    __tablename__ = "proposed_file_changes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    change_request_id = Column(
        Integer,
        ForeignKey("change_requests.id"),
        nullable=False,
        index=True
    )

    file_path = Column(
        String(1000),
        nullable=False
    )

    reason = Column(
        Text,
        nullable=False
    )

    original_code = Column(
        Text,
        nullable=False
    )

    proposed_code = Column(
        Text,
        nullable=False
    )

    change_request = relationship(
        "ChangeRequest",
        back_populates="files"
    )