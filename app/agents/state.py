from typing import TypedDict

from app.schemas.citation import SourceCitation


class AgentState(TypedDict, total=False):

    user_request: str

    repository_id: int

    task_type: str

    relevant_files: list[str]

    context: str

    analysis: str

    proposed_changes: dict

    review: dict

    approval_status: str

    test_result: str

    final_response: dict | str

    citations: list[SourceCitation]