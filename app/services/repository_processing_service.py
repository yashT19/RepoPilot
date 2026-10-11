from pathlib import Path

from app.repository_processing.parser import RepositoryParser
from app.repository_processing.chunker import CodeChunker
from app.ai.embedding_service import EmbeddingService
from app.vector_store.faiss_store import FAISSVectorStore

class RepositoryProcessingService:
    def __init__(self):
        self.parser = RepositoryParser()
        self.chunker = CodeChunker()
        self.embedding_service = EmbeddingService()

        # Determine embedding dimension dynamically
        sample_embedding = self.embedding_service.generate_embedding(
            "sample text"
        )

        self.vector_store = FAISSVectorStore(
            dimension=len(sample_embedding)
        )
    def process_repository(
        self,
        repository_path: Path,
         repository_id: int
    ):

        # 1. Parse repository
        documents = self.parser.parse_repository(
            repository_path
        )
        all_chunks = []

        for document in documents:
            chunks = self.chunker.chunk_document(
                document,
                repository_id=repository_id
            )

            all_chunks.extend(chunks)
          # 3. Generate embeddings
        texts = [
            chunk.content
            for chunk in all_chunks
        ]

        if texts:

            embeddings = (
                self.embedding_service.generate_embeddings(
                    texts
                )
            )    

         # 4. Store embeddings + chunks
            self.vector_store.add(
                 repository_id=repository_id,
    embeddings=embeddings,
    chunks=all_chunks
            )
            self.vector_store.save(
    repository_id
)

        return {
            "documents": len(documents),
            "chunks": len(all_chunks)
        }