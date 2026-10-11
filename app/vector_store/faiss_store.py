import pickle
from pathlib import Path

import faiss
import numpy as np

from app.schemas.chunk import CodeChunk


class FAISSVectorStore:

    def __init__(
        self,
        dimension: int,
        storage_dir: str = "storage/vector_store"
    ):
        self.dimension = dimension

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # Repository-specific indexes
        self.indexes: dict[int, faiss.Index] = {}

        # Repository-specific chunks
        self.chunks: dict[int, list[CodeChunk]] = {}

    # --------------------------------------------------
    # Get or create repository index
    # --------------------------------------------------

    def _get_index(
        self,
        repository_id: int
    ):

        if repository_id not in self.indexes:

            self.indexes[repository_id] = (
                faiss.IndexFlatIP(self.dimension)
            )

            self.chunks[repository_id] = []

        return self.indexes[repository_id]

    # --------------------------------------------------
    # Add embeddings
    # --------------------------------------------------

    def add(
        self,
        repository_id: int,
        embeddings,
        chunks: list[CodeChunk]
    ):

        index = self._get_index(
            repository_id
        )

        vectors = np.asarray(
            embeddings,
            dtype="float32"
        )

        index.add(vectors)

        self.chunks[repository_id].extend(
            chunks
        )

    # --------------------------------------------------
    # Search repository
    # --------------------------------------------------

    def search(
    self,
    repository_id: int,
    query_embedding,
    top_k: int = 5
):

    # --------------------------------------------------
    # Load repository index from disk if not in memory
    # --------------------------------------------------

        if repository_id not in self.indexes:

           loaded = self.load(
            repository_id
        )

           if not loaded:
             return []

    # --------------------------------------------------
    # Get repository-specific index
    # --------------------------------------------------

        index = self.indexes[
        repository_id
    ]

        repository_chunks = self.chunks[
        repository_id
    ]

    # --------------------------------------------------
    # Check if repository contains vectors
    # --------------------------------------------------

        if index.ntotal == 0:
           return []

    # --------------------------------------------------
    # Convert query embedding
    # --------------------------------------------------

        query_vector = np.asarray(
        [query_embedding],
        dtype="float32"
    )

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

        actual_top_k = min(
        top_k,
        index.ntotal
    )

        scores, indices = index.search(
        query_vector,
        actual_top_k
    )

    # --------------------------------------------------
    # Build results
    # --------------------------------------------------

        results = []

        for score, chunk_index in zip(
        scores[0],
        indices[0]
    ):

            if chunk_index == -1:
               continue

            results.append({
            "score": float(score),
            "chunk": repository_chunks[
                chunk_index
            ]
        })

        return results

        
    def save(
        self,
        repository_id: int
    ):

        if repository_id not in self.indexes:
            return

        repository_dir = (
            self.storage_dir
            / str(repository_id)
        )

        repository_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        index_path = (
            repository_dir
            / "index.faiss"
        )

        chunks_path = (
            repository_dir
            / "chunks.pkl"
        )

        # Save FAISS index
        faiss.write_index(
            self.indexes[repository_id],
            str(index_path)
        )

        # Save chunk metadata
        with open(
            chunks_path,
            "wb"
        ) as file:

            pickle.dump(
                self.chunks[repository_id],
                file
            )

    # --------------------------------------------------
    # Load repository index
    # --------------------------------------------------

    def load(
        self,
        repository_id: int
    ):

        repository_dir = (
            self.storage_dir
            / str(repository_id)
        )

        index_path = (
            repository_dir
            / "index.faiss"
        )

        chunks_path = (
            repository_dir
            / "chunks.pkl"
        )

        if not index_path.exists():
            return False

        if not chunks_path.exists():
            return False

        # Load FAISS index
        self.indexes[repository_id] = (
            faiss.read_index(
                str(index_path)
            )
        )

        # Load chunks
        with open(
            chunks_path,
            "rb"
        ) as file:

            self.chunks[repository_id] = (
                pickle.load(file)
            )

        return True

    # --------------------------------------------------
# Reset repository index
# --------------------------------------------------

    def reset_repository(
    self,
    repository_id: int
):

    # ----------------------------------------------
    # 1. Remove index from memory
    # ----------------------------------------------

        self.indexes.pop(
        repository_id,
        None
    )

    # ----------------------------------------------
    # 2. Remove chunks from memory
    # ----------------------------------------------

        self.chunks.pop(
        repository_id,
        None
    )

    # ----------------------------------------------
    # 3. Locate repository vector store directory
    # ----------------------------------------------

        repository_dir = (
        self.storage_dir
        / str(repository_id)
    )

    # ----------------------------------------------
    # 4. Delete saved FAISS index
    # ----------------------------------------------

        index_path = (
        repository_dir
        / "index.faiss"
    )

        if index_path.exists():
           index_path.unlink()

    # ----------------------------------------------
    # 5. Delete saved chunks
    # ----------------------------------------------

        chunks_path = (
        repository_dir
        / "chunks.pkl"
    )

        if chunks_path.exists():
           chunks_path.unlink()

    # ----------------------------------------------
    # 6. Remove empty repository directory
    # ----------------------------------------------

        if repository_dir.exists():

            try:
               repository_dir.rmdir()

            except OSError:
            # Directory is not empty
               pass