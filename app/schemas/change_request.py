from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from app.models.change_request import ChangeRequestStatus


# ==================================================
# Proposed File Change
# ==================================================

class ProposedFileChangeResponse(BaseModel):

    id: int

    file_path: str
    reason: str

    original_code: str
    proposed_code: str

    model_config = ConfigDict(
        from_attributes=True
    )


# ==================================================
# Change Request Response
# ==================================================

class ChangeRequestResponse(BaseModel):

    id: int

    repository_id: int

    user_request: str

    status: ChangeRequestStatus

    created_at: datetime

    updated_at: datetime

    files: List[
        ProposedFileChangeResponse
    ]

    model_config = ConfigDict(
        from_attributes=True
    )


# ==================================================
# Human Approval Request
# ==================================================

class ChangeRequestDecision(BaseModel):

    approved: bool