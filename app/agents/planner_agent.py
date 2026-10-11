from app.ai.llm_service import LLMService
from langsmith import traceable

class PlannerAgent:

# --------------------------------------------------
# Supported Task Types
# --------------------------------------------------

 VALID_TASK_TYPES = {
    "ANALYSIS",
    "CODE_MODIFICATION",
    "CODE_REVIEW",
    "TESTING"
}

 def __init__(
    self,
    llm_service: LLMService
):
    self.llm_service = llm_service

 @traceable(
    name="Planner Agent",
    run_type="chain"
)
 def plan(
    self,
    user_request: str
) -> str:

    prompt = f"""

You are the Planner Agent of an AI Software Engineering Agent.

Analyze the user's request and classify it into exactly
one of these categories:

ANALYSIS
CODE_MODIFICATION
CODE_REVIEW
TESTING

Classification rules:

* ANALYSIS:
  Use when the user wants to understand, explain,
  analyze, trace, or describe existing code.

* CODE_MODIFICATION:
  Use when the user wants to add, change, fix,
  remove, or modify existing code.

* CODE_REVIEW:
  Use when the user wants the repository or code
  reviewed for bugs, code quality issues, security
  problems, validation issues, performance concerns,
  or best-practice violations.

* TESTING:
  Use when the user wants to create, generate,
  execute, or analyze tests.

User request:
{user_request}

Return ONLY the category name.
"""

    result = self.llm_service.generate(
        prompt
    )

    task_type = result.strip().upper()

    # --------------------------------------------------
    # Validate LLM Response
    # --------------------------------------------------

    if task_type not in self.VALID_TASK_TYPES:

        return "ANALYSIS"

    return task_type

