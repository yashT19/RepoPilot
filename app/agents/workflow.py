from langgraph.graph import StateGraph, END
from langsmith import traceable

from app.agents.state import AgentState
from app.agents.planner_agent import PlannerAgent
from app.agents.code_analysis_agent import CodeAnalysisAgent
from app.agents.code_modification_agent import (
CodeModificationAgent,
)
from app.agents.code_review_agent import CodeReviewAgent
from app.agents.testing_agent import TestingAgent

from app.services.change_request_service import (
ChangeRequestService,
)

class AgentWorkflow:
  def __init__(
    self,
    planner_agent: PlannerAgent,
    code_analysis_agent: CodeAnalysisAgent,
    code_modification_agent: CodeModificationAgent,
    code_review_agent: CodeReviewAgent,
    testing_agent: TestingAgent,
    change_request_service: ChangeRequestService,
):

    # --------------------------------------------------
    # Agents and Services
    # --------------------------------------------------

    self.planner_agent = planner_agent

    self.code_analysis_agent = code_analysis_agent

    self.code_modification_agent = (
        code_modification_agent
    )

    self.code_review_agent = code_review_agent

    self.testing_agent = testing_agent

    self.change_request_service = (
        change_request_service
    )

    # --------------------------------------------------
    # Create LangGraph Workflow
    # --------------------------------------------------

    graph = StateGraph(AgentState)

    # --------------------------------------------------
    # Add Nodes
    # --------------------------------------------------

    graph.add_node(
        "planner",
        self.planner_node,
    )

    graph.add_node(
        "code_analysis",
        self.code_analysis_node,
    )

    graph.add_node(
        "code_modification",
        self.code_modification_node,
    )

    graph.add_node(
        "code_review",
        self.code_review_node,
    )

    graph.add_node(
        "testing",
        self.testing_node,
    )

    # --------------------------------------------------
    # Entry Point
    # --------------------------------------------------

    graph.set_entry_point(
        "planner"
    )

    # --------------------------------------------------
    # Conditional Routing
    # --------------------------------------------------

    graph.add_conditional_edges(
        "planner",
        self.route_after_planner,
        {
            "ANALYSIS": "code_analysis",
            "CODE_MODIFICATION": (
                "code_modification"
            ),
            "CODE_REVIEW": "code_review",
            "TESTING": "testing",
            "END": END,
        },
    )

    # --------------------------------------------------
    # Endpoints
    # --------------------------------------------------

    graph.add_edge(
        "code_analysis",
        END,
    )

    graph.add_edge(
        "code_modification",
        END,
    )

    graph.add_edge(
        "code_review",
        END,
    )

    graph.add_edge(
        "testing",
        END,
    )

    # --------------------------------------------------
    # Compile Graph
    # --------------------------------------------------

    self.graph = graph.compile()

# ==================================================
# Planner Node
# ==================================================

  @traceable(
    name="Planner Agent",
    run_type="chain",
)
  def planner_node(
    self,
    state: AgentState,
):

    task_type = self.planner_agent.plan(
        state["user_request"]
    )

    return {
        "task_type": task_type,
    }

# ==================================================
# Routing
# ==================================================

  @traceable(
    name="Task Routing",
    run_type="chain",
)
  def route_after_planner(
    self,
    state: AgentState,
):

    task_type = state["task_type"]

    if task_type == "ANALYSIS":

        return "ANALYSIS"

    if task_type == "CODE_MODIFICATION":

        return "CODE_MODIFICATION"

    if task_type == "CODE_REVIEW":

        return "CODE_REVIEW"

    if task_type == "TESTING":

        return "TESTING"

    return "END"

# ==================================================
# Code Analysis Node
# ==================================================

  @traceable(
    name="Code Analysis Agent",
    run_type="chain",
)
  def code_analysis_node(
    self,
    state: AgentState,
):

    result = (
        self.code_analysis_agent.analyze(
            user_request=state[
                "user_request"
            ],
            repository_id=state[
                "repository_id"
            ],
        )
    )

    return {
        "analysis": result["analysis"],
        "relevant_files": result[
            "relevant_files"
        ],
        "citations": result.get("citations", []),
        "final_response": result["analysis"],
    }

# ==================================================
# Code Review Node
# ==================================================

  @traceable(
    name="Code Review Agent",
    run_type="chain",
)
  def code_review_node(
    self,
    state: AgentState,
):

    result = (
        self.code_review_agent.review(
            user_request=state[
                "user_request"
            ],
            repository_id=state[
                "repository_id"
            ],
        )
    )

    if not result:

        return {
            "review": {},
            "relevant_files": [],
            "citations": result.get("citations", []),
            "final_response": {
                "status": "FAILED",
                "message": (
                    "Code review agent "
                    "returned no result."
                ),
            },
        }

    return {
        "review": result,
        "relevant_files": result.get(
            "relevant_files",
            [],
        ),
        "citations": result.get("citations", []),
        "final_response": result,
    }

# ==================================================
# Code Modification Node
# ==================================================

  @traceable(
    name="Code Modification Agent",
    run_type="chain",
)
  def code_modification_node(
    self,
    state: AgentState,
):

    # --------------------------------------------------
    # Ask Code Modification Agent
    # --------------------------------------------------

    result = (
        self.code_modification_agent.propose_change(
            user_request=state[
                "user_request"
            ],
            repository_id=state[
                "repository_id"
            ],
        )
    )

    # --------------------------------------------------
    # Handle Failure
    # --------------------------------------------------

    if not result:

        return {
            "proposed_changes": {},
            "relevant_files": [],
            "citations": [],
            "final_response": {
                "status": "FAILED",
                "message": (
                    "Code modification agent "
                    "returned no result."
                ),
            },
        }

    # --------------------------------------------------
    # Handle Non-Proposed Result
    # --------------------------------------------------

    if result.get("status") != "PROPOSED":

        return {
            "proposed_changes": result,
            "relevant_files": [],
            "citations": result.get("citations", []),
            "final_response": result,
        }

    # --------------------------------------------------
    # Get Proposed Files
    # --------------------------------------------------

    proposed_files = result.get(
        "files",
        [],
    )

    if not proposed_files:

        return {
            "proposed_changes": result,
            "relevant_files": [],
            "citations": result.get("citations", []),
            "final_response": {
                "status": "FAILED",
                "message": (
                    "The agent proposed "
                    "no file changes."
                ),
            },
        }

    # --------------------------------------------------
    # Save Change Request
    # --------------------------------------------------

    change_request = (
        self.change_request_service
        .create_change_request(
            repository_id=state[
                "repository_id"
            ],
            user_request=state[
                "user_request"
            ],
            proposed_files=proposed_files,
        )
    )

    # --------------------------------------------------
    # Extract Relevant Files
    # --------------------------------------------------

    relevant_files = [
        file["path"]
        for file in proposed_files
        if file.get("path")
    ]

    # --------------------------------------------------
    # Human Approval Response
    # --------------------------------------------------

    approval_response = {
        "status": "PENDING_APPROVAL",
        "change_request_id": (
            change_request.id
        ),
        "summary": result.get(
            "summary",
            "",
        ),
        "message": (
            "Code changes were proposed and "
            "saved. Human approval is required "
            "before the changes can be applied."
        ),
    }

    return {
        "proposed_changes": result,
        "relevant_files": relevant_files,
        "citations": result.get("citations", []),
        "final_response": approval_response,
    }

# ==================================================
# Testing Node
# ==================================================

  @traceable(
    name="Testing Agent",
    run_type="chain",
)
  def testing_node(
    self,
    state: AgentState,
):

    result = (
        self.testing_agent.generate_tests(
            user_request=state[
                "user_request"
            ],
            repository_id=state[
                "repository_id"
            ],
        )
    )

    return {
        "test_result": result,
        "relevant_files": result.get(
            "relevant_files",
            [],
        ),
        "citations": result.get("citations", []),
        "final_response": result,
    }

# ==================================================
# Run Complete Workflow
# ==================================================

  @traceable(
    name="AI Software Engineering Agent",
    run_type="chain",
)
  def run(
    self,
    user_request: str,
    repository_id: int,
):

    initial_state: AgentState = {
        "user_request": user_request,
        "repository_id": repository_id,
    }

    return self.graph.invoke(
        initial_state
    )

