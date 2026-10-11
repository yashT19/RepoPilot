import json

from app.ai.llm_service import LLMService
from app.ai.retriever import CodeRetriever
from app.ai.citations import citations_from_results

from langsmith import traceable
class TestingAgent:

    def __init__(
        self,
        llm_service: LLMService,
        retriever: CodeRetriever
    ):
        self.llm_service = llm_service
        self.retriever = retriever

    # ==================================================
    # Generate Test Cases
    # ==================================================
    
    @traceable(
    name="Testing Agent",
    run_type="chain"
)
    def generate_tests(
        self,
        user_request: str,
        repository_id: int
    ) -> dict:

        # --------------------------------------------------
        # 1. Retrieve relevant code
        # --------------------------------------------------

        results = self.retriever.retrieve(
            query=user_request,
            repository_id=repository_id
        )

        # --------------------------------------------------
        # 2. Handle no context
        # --------------------------------------------------

        if not results:

            return {
                "status": "NO_CONTEXT",
                "summary": "",
                "test_cases": [],
                "citations": [],
                "message": (
                    "I could not find relevant code "
                    "in the repository."
                )
            }

        # --------------------------------------------------
        # 3. Build code context
        # --------------------------------------------------

        context_parts = []
        relevant_files = []
        citations = citations_from_results(results)

        for result in results:

            chunk = result["chunk"]
            file_path = chunk.file_path

            if file_path not in relevant_files:
                relevant_files.append(file_path)

            context_parts.append(
                f"""
FILE: {file_path}
Citation: [{chunk.file_path}:{chunk.start_line}-{chunk.end_line}]

CODE:
{chunk.content}
"""
            )

        context = "\n".join(context_parts)

        # --------------------------------------------------
        # 4. Build testing prompt
        # --------------------------------------------------

        prompt = f"""
You are an expert Software Test Engineer.

User request:
{user_request}

Relevant repository code:

{context}

Analyze the code and generate useful test cases.

Consider:

- Normal scenarios
- Edge cases
- Invalid input
- Boundary conditions
- Error scenarios

Return ONLY valid JSON in exactly this format:

{{
    "summary": "Brief summary of the testing strategy",
    "test_cases": [
        {{
            "name": "Test case name",
            "file": "file path",
            "scenario": "What is being tested",
            "input": "Test input",
            "expected_result": "Expected behavior",
            "priority": "HIGH"
        }}
    ]
}}

Priority must be exactly one of:

HIGH
MEDIUM
LOW

Do not include markdown.
Do not include ```json.
Do not include any text outside the JSON.
Every test case grounded in repository code must cite the supplied source
using [path:start-end]. Use only supplied context and say when it is
insufficient; never invent citations.
"""

        # --------------------------------------------------
        # 5. Call LLM
        # --------------------------------------------------

        response = self.llm_service.generate(
            prompt
        )

        # --------------------------------------------------
        # 6. Parse LLM response
        # --------------------------------------------------

        try:

            test_result = json.loads(
                response
            )

        except (
            json.JSONDecodeError,
            TypeError
        ):

            return {
                "status": "INVALID_LLM_RESPONSE",
                "summary": "",
                "test_cases": [],
                "relevant_files": relevant_files,
                "citations": citations,
                "message": (
                    "The model returned an invalid "
                    "testing response."
                )
            }

        # --------------------------------------------------
        # 7. Return structured result
        # --------------------------------------------------

        return {
            "status": "COMPLETED",
            "summary": test_result.get(
                "summary",
                ""
            ),
            "test_cases": test_result.get(
                "test_cases",
                []
            ),
            "relevant_files": relevant_files,
            "citations": citations
        }