from fastapi import APIRouter

from app.core.container import container


router = APIRouter(
    prefix="/agent",
    tags=["Agent"]
)


@router.post("")
def run_agent(
    repository_id: int,
    question: str
):

    result = container.agent_workflow.run(
        user_request=question,
        repository_id=repository_id
    )

    return {
        "question": question,
        "repository_id": repository_id,
        "task_type": result.get("task_type"),
        "relevant_files": result.get(
            "relevant_files",
            []
        ),
        "answer": result.get(
            "final_response"
        ),
        "citations": result.get("citations", [])
    }