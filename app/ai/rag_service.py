from app.ai.llm_service import LLMService
from app.ai.prompt_builder import CodePromptBuilder
from app.ai.retriever import CodeRetriever

class RAGService:
    def __init__(
        self,
        retriever: CodeRetriever,
        prompt_builder: CodePromptBuilder,
        llm_service: LLMService
    ):
        self.retriever = retriever
        self.prompt_builder = prompt_builder
        self.llm_service = llm_service

    def answer(
        self,
        question: str,
        top_k: int = 5
    ) -> str:

        retrieved_chunks = self.retriever.retrieve(
            question,
            top_k=top_k
        )
        if not retrieved_chunks:
            return (
                "I could not find relevant code "
                "in the repository."
            )

        prompt = self.prompt_builder.build_prompt(
            question,
            retrieved_chunks
        )

        return self.llm_service.generate(prompt)    
    
