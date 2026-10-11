from fastapi import APIRouter, HTTPException

from app.core.container import container


router = APIRouter(
    prefix="/change-requests",
    tags=["Change Requests"]
)


# ==================================================
# Approve Change Request
# ==================================================

@router.post("/{change_request_id}/approve")
def approve_change_request(
    change_request_id: int
):

    try:

        change_request = (
            container.change_request_service
            .approve_change_request(
                change_request_id
            )
        )

        return {
            "change_request_id": change_request.id,
            "repository_id": change_request.repository_id,
            "status": change_request.status.value,
            "message": (
                "Change request approved and "
                "code changes applied successfully."
            )
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ==================================================
# Reject Change Request
# ==================================================

@router.post("/{change_request_id}/reject")
def reject_change_request(
    change_request_id: int
):

    try:

        change_request = (
            container.change_request_service
            .reject_change_request(
                change_request_id
            )
        )

        return {
            "change_request_id": change_request.id,
            "repository_id": change_request.repository_id,
            "status": change_request.status.value,
            "message": (
                "Change request rejected. "
                "No code changes were applied."
            )
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )