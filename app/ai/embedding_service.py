from sentence_transformers import SentenceTransformer
class EmbeddingService:

    def __init__(self,
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
         self.model = SentenceTransformer(model_name)

    def generate_embedding(self, text:str):
           return self.model.encode(
            text,
            normalize_embeddings=True
        )
    def generate_embeddings(self, texts: list[str]):

        return self.model.encode(
            texts,
            normalize_embeddings=True
        )     