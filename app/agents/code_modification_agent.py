import json

from app.ai.llm_service import LLMService
from app.ai.retriever import CodeRetriever
from app.ai.citations import citations_from_results
from langsmith import traceable

class CodeModificationAgent:

    def __init__(
        self,
        llm_service: LLMService,
        retriever: CodeRetriever
    ):
        self.llm_service = llm_service
        self.retriever = retriever
    @traceable(
    name="Code Modification Agent",
    run_type="chain"
)
    def propose_change(
        self,
        user_request: str,
        repository_id: int
    ) -> dict:

        # --------------------------------------------------
        # 1. Retrieve relevant repository code
        # --------------------------------------------------

        retrieved_chunks = self.retriever.retrieve(
            repository_id=repository_id,
            query=user_request,
            top_k=5
        )

        if not retrieved_chunks:
            return {
                "status": "NO_CONTEXT",
                "files": [],
                "summary": "",
                "citations": [],
                "message": (
                    "I could not find relevant code "
                    "in the repository."
                )
            }

        # --------------------------------------------------
        # 2. Build repository context
        # --------------------------------------------------

        context_parts = []
        citations = citations_from_results(retrieved_chunks)

        for result in retrieved_chunks:

            chunk = result["chunk"]

            context_parts.append(
                f"""
File: {chunk.file_path}
Citation: [{chunk.file_path}:{chunk.start_line}-{chunk.end_line}]
Language: {chunk.language}

Code:
{chunk.content}
"""
            )

        context = "\n\n".join(context_parts)

        # --------------------------------------------------
        # 3. Ask LLM to propose modification
        # --------------------------------------------------

        prompt = f"""
You are the Code Modification Agent in an
AI Software Engineering Assistant.

The user wants to modify an existing repository.

User request:
{user_request}

Repository context:
{context}

Your task is to propose a code modification.

IMPORTANT RULES:

1. Only modify files that appear in the provided context.
2. Do not invent files.
3. Do not invent classes or methods.
4. Preserve the existing coding style where possible.
5. Do not modify unrelated code.
6. Explain why the change is required.
7. Do NOT apply the change.
8. The change will be reviewed by a human before
   it can be applied.
9. Return ONLY valid JSON.
10. Cite the original code for every proposed change using [path:start-end].
11. Citations must refer to the supplied original code, never proposed code.
12. If context is insufficient, say so and return no fabricated citation.

Return exactly this structure:

{{
    "files": [
        {{
            "path": "exact file path",
            "reason": "why this file needs modification",
            "original_code": "relevant existing code",
            "proposed_code": "modified code"
        }}
    ],
    "summary": "short explanation of the proposed change"
}}
"""

        print(
            "\n\n******** MODIFICATION AGENT START ********"
        )

        print(
            "User request:",
            user_request
        )

        print(
            "Repository ID:",
            repository_id
        )

        response = self.llm_service.generate(
            prompt
        )

        print(
            "\n========== LLM MODIFICATION RESPONSE =========="
        )

        print(response)

        print(
            "================================================\n"
        )

        # --------------------------------------------------
        # 4. Validate LLM response
        # --------------------------------------------------

        if not response:

            return {
                "status": "INVALID_LLM_RESPONSE",
                "files": [],
                "summary": "",
                "citations": citations,
                "message": (
                    "The LLM returned an empty response."
                )
            }

        response = response.strip()

        # --------------------------------------------------
        # Remove Markdown JSON code fences
        # --------------------------------------------------

        if response.startswith("```json"):

            response = response[
                len("```json"):
            ].strip()

        elif response.startswith("```"):

            response = response[
                len("```"):
            ].strip()

        if response.endswith("```"):

            response = response[:-3].strip()

        # --------------------------------------------------
        # Parse JSON
        # --------------------------------------------------

        try:

            result = json.loads(response)

        except json.JSONDecodeError as exc:

            print(
                "JSON parsing failed:",
                exc
            )

            return {
                "status": "INVALID_LLM_RESPONSE",
                "files": [],
                "summary": "",
                "citations": citations,
                "message": (
                    "The model returned an invalid "
                    "modification proposal."
                )
            }

        # --------------------------------------------------
        # Validate proposal structure
        # --------------------------------------------------

        if not isinstance(result, dict):

            return {
                "status": "INVALID_LLM_RESPONSE",
                "files": [],
                "summary": "",
                "citations": citations,
                "message": (
                    "The model response must be a JSON object."
                )
            }

        files = result.get(
            "files",
            []
        )

        summary = result.get(
            "summary",
            ""
        )

        if not isinstance(files, list):

            return {
                "status": "INVALID_LLM_RESPONSE",
                "files": [],
                "summary": "",
                "message": (
                    "'files' must be a list."
                )
            }

        # --------------------------------------------------
        # 5. Successful proposal
        # --------------------------------------------------

        return {
            "status": "PROPOSED",
            "files": files,
            "summary": summary,
            "citations": citations
        }