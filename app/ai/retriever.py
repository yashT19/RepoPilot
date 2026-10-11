from langsmith import traceable

from app.ai.embedding_service import EmbeddingService
from app.vector_store.faiss_store import FAISSVectorStore


class CodeRetriever:

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: FAISSVectorStore
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    # ==================================================
    # Retrieve Relevant Code
    # ==================================================

    @traceable(
        name="Code Retrieval",
        run_type="retriever"
    )
    def retrieve(
        self,
        repository_id: int,
        query: str,
        top_k: int = 5
    ):

        # --------------------------------------------------
        # Generate query embedding
        # --------------------------------------------------

        query_embedding = (
            self.embedding_service.generate_embedding(
                query
            )
        )

        # --------------------------------------------------
        # Search vector store
        # --------------------------------------------------

        results = self.vector_store.search(
            repository_id=repository_id,
            query_embedding=query_embedding,
            top_k=top_k
        )

        # --------------------------------------------------
        # Return retrieved code chunks
        # --------------------------------------------------

        for result in results:
            result["citation"] = result["chunk"].citation(
                score=result["score"]
            ).model_dump()
            result["retrieval_source"] = "faiss"

        return results