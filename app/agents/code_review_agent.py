import json

from app.ai.llm_service import LLMService
from app.ai.retriever import CodeRetriever
from app.ai.citations import citations_from_results
from langsmith import traceable

class CodeReviewAgent:

    def __init__(
        self,
        llm_service: LLMService,
        retriever: CodeRetriever
    ):
        self.llm_service = llm_service
        self.retriever = retriever

    # ==================================================
    # Review Code
    # ==================================================
    @traceable(
    name="Code Review Agent",
    run_type="chain"
)
    def review(
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
                "issues": [],
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
        citations = citations_from_results(results)

        relevant_files = []

        for result in results:

            chunk = result["chunk"]

            file_path = chunk.file_path

            if file_path not in relevant_files:
                relevant_files.append(
                    file_path
                )

            context_parts.append(
                f"""
FILE: {file_path}
Citation: [{chunk.file_path}:{chunk.start_line}-{chunk.end_line}]

CODE:
{chunk.content}
"""
            )

        context = "\n".join(
            context_parts
        )

        # --------------------------------------------------
        # 4. Build review prompt
        # --------------------------------------------------

        prompt = f"""
You are an expert Senior Software Engineer
performing a code review.

User request:
{user_request}

Relevant repository code:

{context}

Review the code carefully for:

- Bugs
- Security issues
- Performance problems
- Poor error handling
- Code quality issues
- Edge cases
- Maintainability problems

Return ONLY valid JSON in exactly this format:

{{
    "summary": "Brief overall review summary",
    "issues": [
        {{
            "severity": "HIGH",
            "file": "file path",
            "issue": "Description of the problem",
            "suggestion": "How to improve it"
        }}
    ]
}}

Severity must be exactly one of:

HIGH
MEDIUM
LOW

If no issues are found, return:

{{
    "summary": "No significant issues found.",
    "issues": []
}}

Do not include markdown.
Do not include ```json.
Do not include any text outside the JSON.
Every summary, issue, and suggestion based on repository code must cite
the supplied source using [path:start-end]. Use only supplied context and
say when it is insufficient; never invent citations.
"""

        # --------------------------------------------------
        # 5. Call LLM
        # --------------------------------------------------

        response = self.llm_service.generate(
            prompt
        )

        # --------------------------------------------------
        # 6. Parse response
        # --------------------------------------------------

        try:

            review_result = json.loads(
                response
            )

        except (
            json.JSONDecodeError,
            TypeError
        ):

            return {
                "status": "INVALID_LLM_RESPONSE",
                "summary": "",
                "issues": [],
                "relevant_files": relevant_files,
                "citations": citations,
                "message": (
                    "The model returned an invalid "
                    "code review response."
                )
            }

        # --------------------------------------------------
        # 7. Return review result
        # --------------------------------------------------

        return {
            "status": "COMPLETED",
            "summary": review_result.get(
                "summary",
                ""
            ),
            "issues": review_result.get(
                "issues",
                []
            ),
            "relevant_files": relevant_files,
            "citations": citations
        }