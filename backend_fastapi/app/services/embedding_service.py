from sentence_transformers import SentenceTransformer

class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, text: str):

        if not text:
            return []

        embedding = self.model.encode(text)

        return embedding.tolist()

    def build_index(self):
        # We'll implement this later after storing embeddings.
        pass