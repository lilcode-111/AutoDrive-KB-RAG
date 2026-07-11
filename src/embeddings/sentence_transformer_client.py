from typing import List
from sentence_transformers import SentenceTransformer
from src.embeddings.embedding_client import EmbeddingClient

class SentenceTransformerEmbeddingClient(EmbeddingClient):
    """
    Sentence-transformers based embedding client.

    This client is responsible for:
    1. loading a local / HuggingFace sentence-transformers model;
    2. converting chunk texts into normalized dense vectors;
    3. converting user queries into normalized dense vectors.

    Normalized vectors make cosine similarity easier in Day3:
    cosine_similarity(a, b) == dot_product(a, b)
    when both vectors have L2 norm = 1.
    """
    def __init__(self,
                 model_name:str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 batch_size:int = 32,
                 normalize_embeddings: bool = True) -> None:
        self.model_name = model_name
        self.batch_size = batch_size
        self.normalize_embeddings = normalize_embeddings
        self.model = SentenceTransformer(model_name)
    
    def embed_texts(self,texts:List[str])->List[List[float]]:
        if not texts:
            return []
        
        cleaned_texts = []
        for text in texts:
            if text is None:
                cleaned_texts.append("")
            else:
                cleaned_texts.append(str(text))
        
        vectors = self.model.encode(
            cleaned_texts,
            batch_size = self.batch_size,
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return vectors.tolist()
    
    def embed_query(self, query: str) -> List[float]:
        if query is None or not str(query).strip():
            raise ValueError("query must be a non-empty string")
        vectors = self.embed_texts([query])
        return vectors[0]

    def get_embedding_dimension(self)->int:
        dimension = self.model.get_embedding_dimension()
        if dimension is None:
            raise RuntimeError("Failed to get embedding dimension from sentence-transformers model.")

        return dimension
