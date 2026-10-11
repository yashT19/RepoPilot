from sqlalchemy.orm import Session

from app.models.repository import Repository
from app.models.change_request import (
ChangeRequest,
ChangeRequestStatus
)
from app.models.proposed_file_change import (
ProposedFileChange
)
from app.services.code_change_applier import CodeChangeApplier

class ChangeRequestService:


 def __init__(
    self,
    db: Session,
    code_change_applier: CodeChangeApplier
):
    self.db = db
    self.code_change_applier = code_change_applier

# ==================================================
# Create Change Request
# ==================================================

 def create_change_request(
    self,
    repository_id: int,
    user_request: str,
    proposed_files: list[dict]
) -> ChangeRequest:

    # ----------------------------------------------
    # Create main change request
    # ----------------------------------------------

    change_request = ChangeRequest(
        repository_id=repository_id,
        user_request=user_request,
        status=ChangeRequestStatus.PENDING
    )

    self.db.add(change_request)

    # Get change_request.id without committing yet
    self.db.flush()

    # ----------------------------------------------
    # Save proposed file changes
    # ----------------------------------------------

    for file in proposed_files:

        proposed_file_change = ProposedFileChange(
            change_request_id=change_request.id,
            file_path=file["path"],
            reason=file["reason"],
            original_code=file["original_code"],
            proposed_code=file["proposed_code"]
        )

        self.db.add(proposed_file_change)

    # ----------------------------------------------
    # Commit everything
    # ----------------------------------------------

    self.db.commit()

    self.db.refresh(change_request)

    return change_request

# ==================================================
# Get Change Request
# ==================================================

 def get_change_request(
    self,
    change_request_id: int
) -> ChangeRequest | None:

    return (
        self.db.query(ChangeRequest)
        .filter(
            ChangeRequest.id == change_request_id
        )
        .first()
    )

# ==================================================
# Reject Change Request
# ==================================================

 def reject_change_request(
    self,
    change_request_id: int
) -> ChangeRequest:

    change_request = self.get_change_request(
        change_request_id
    )

    if not change_request:
        raise ValueError(
            "Change request not found."
        )

    # Only PENDING requests can be rejected
    if (
        change_request.status
        != ChangeRequestStatus.PENDING
    ):
        raise ValueError(
            "Only pending change requests "
            "can be rejected."
        )

    change_request.status = (
        ChangeRequestStatus.REJECTED
    )

    self.db.commit()

    self.db.refresh(change_request)

    return change_request

# ==================================================
# Approve and Apply Change Request
# ==================================================

 def approve_change_request(
    self,
    change_request_id: int
) -> ChangeRequest:

    # ----------------------------------------------
    # 1. Get Change Request
    # ----------------------------------------------

    change_request = self.get_change_request(
        change_request_id
    )

    if not change_request:
        raise ValueError(
            "Change request not found."
        )

    # ----------------------------------------------
    # 2. Validate Status
    # ----------------------------------------------

    if (
        change_request.status
        != ChangeRequestStatus.PENDING
    ):
        raise ValueError(
            "Only pending change requests "
            "can be approved."
        )

    # ----------------------------------------------
    # 3. Get Repository
    # ----------------------------------------------

    repository = (
        self.db.query(Repository)
        .filter(
            Repository.id
            == change_request.repository_id
        )
        .first()
    )

    if not repository:
        raise ValueError(
            "Repository not found."
        )

    # ----------------------------------------------
    # 4. Get Proposed File Changes
    # ----------------------------------------------

    proposed_changes = (
        self.db.query(ProposedFileChange)
        .filter(
            ProposedFileChange.change_request_id
            == change_request.id
        )
        .all()
    )

    if not proposed_changes:
        raise ValueError(
            "No proposed file changes found."
        )

    try:

        # ------------------------------------------
        # 5. Mark request as APPROVED
        # ------------------------------------------

        change_request.status = (
            ChangeRequestStatus.APPROVED
        )

        self.db.commit()

        # ------------------------------------------
        # 6. Apply each proposed file change
        # ------------------------------------------

        for proposed_change in proposed_changes:

            apply_result = (
                self.code_change_applier.apply_change(
                    repository_path=repository.storage_path,
                    file_path=proposed_change.file_path,
                    original_code=(
                        proposed_change.original_code
                    ),
                    proposed_code=(
                        proposed_change.proposed_code
                    )
                )
            )

            # Stop immediately if applying fails
            if not apply_result["success"]:

                raise ValueError(
                    apply_result["message"]
                )

        # ------------------------------------------
        # 7. All changes applied successfully
        # ------------------------------------------

        change_request.status = (
            ChangeRequestStatus.APPLIED
        )

        self.db.commit()

        self.db.refresh(change_request)

        return change_request

    except Exception as error:

        # ------------------------------------------
        # 8. Roll back failed transaction
        # ------------------------------------------

        self.db.rollback()

        # ------------------------------------------
        # 9. Mark request as FAILED
        # ------------------------------------------

        failed_change_request = (
            self.get_change_request(
                change_request_id
            )
        )

        if failed_change_request:

            failed_change_request.status = (
                ChangeRequestStatus.FAILED
            )

            self.db.commit()

        raise ValueError(
            f"Failed to apply changes: {str(error)}"
        )

# ==================================================
# Update Status
# ==================================================

 def update_status(
    self,
    change_request: ChangeRequest,
    status: ChangeRequestStatus
) -> ChangeRequest:

    change_request.status = status

    self.db.commit()

    self.db.refresh(change_request)

    return change_request
