from app.ai.llm_service import LLMService
from app.ai.retriever import CodeRetriever
from app.ai.citations import citations_from_results
from langsmith import traceable

class CodeAnalysisAgent:

    def __init__(
        self,
        llm_service: LLMService,
        retriever: CodeRetriever
    ):
        self.llm_service = llm_service
        self.retriever = retriever
    @traceable(
    name="Code Analysis Agent",
    run_type="chain"
)
    def analyze(
        self,
        user_request: str,
        repository_id: int
    ) -> dict:

        # 1. Retrieve relevant code
        retrieved_chunks = self.retriever.retrieve(
            repository_id=repository_id,
            query=user_request,
            top_k=5
        )

        if not retrieved_chunks:
            return {
                "analysis": (
                    "I could not find relevant code "
                    "in the repository."
                ),
                "relevant_files": [],
                "citations": []
            }

        citations = citations_from_results(retrieved_chunks)

        # 2. Build repository context
        context_parts = []
        relevant_files = []

        for result in retrieved_chunks:

            chunk = result["chunk"]

            file_path = str(chunk.file_path)

            if file_path not in relevant_files:
                relevant_files.append(file_path)

            context_parts.append(
                f"""
File: {file_path}
Citation: [{chunk.file_path}:{chunk.start_line}-{chunk.end_line}]
Language: {chunk.language}

Code:
{chunk.content}
"""
            )

        context = "\n\n".join(context_parts)

        # 3. Ask the LLM to analyze the code
        prompt = f"""
You are the Code Analysis Agent in an
AI Software Engineering Assistant.

Analyze the repository code using the context below.

User request:
{user_request}

Repository context:
{context}

Instructions:

1. Explain what the relevant code does.
2. Identify the important classes, methods, and logic.
3. Mention relevant file paths.
4. Explain how the components interact.
5. Do not invent files or code that are not
   present in the provided context.
6. If the context is insufficient, clearly say so.
7. Cite every repository-based claim using [path:start-end].
8. Use only the supplied context and never invent citations.

Provide a clear software-engineering explanation.
"""

        analysis = self.llm_service.generate(prompt)

        return {
            "analysis": analysis,
            "relevant_files": relevant_files,
            "citations": citations
        }