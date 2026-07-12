from typing import Any,Dict,List
import numpy as np

class InMemoryVectorIndex:
    """
    A simple in-memory vector index for Week11 retrieval.

    This index stores:
    1. chunk dictionaries
    2. corresponding embedding vectors

    It supports top_k search by dot product.

    Since our embedding vectors are normalized in SentenceTransformerEmbeddingClient,
    dot product is equivalent to cosine similarity.
    """

    def __init__(self) -> None:
        self.chunks: List[Dict[str,Any]] = []
        self.vectors: List[List[float]] = []
        self.embedding_dimension: int|None = None

    def add_chunks(
        self,
        chunks:List[Dict[str,Any]],
        vectors:List[List[float]]
    )->None:
        """
        Add chunks and their embedding vectors into the index.

        Args:
            chunks: List of chunk dictionaries.
            vectors: List of embedding vectors. Must have the same length as chunks.
        """
        if len(chunks) != len(vectors):
            raise ValueError(
                f"chunks and vectors must have the same length, "
                f"got len(chunks)={len(chunks)}, len(vectors)={len(vectors)}"
            )

        if not chunks:
            return
        
        for vector in vectors:
            if not vector:
                raise ValueError("embedding vector must not be empty")

            vector_dim = len(vector)

            if self.embedding_dimension is None:
                self.embedding_dimension = vector_dim
            elif vector_dim!=self.embedding_dimension:
                raise ValueError(
                    f"all vectors must have the same dimension, "
                    f"expected {self.embedding_dimension}, got {vector_dim}"
                )
            
        self.chunks.extend(chunks)
        self.vectors.extend(vectors)

    def search(
        self,
        query_vector:List[float],
        top_k:int = 5,
    )->List[Dict[str,Any]]:
        """
        Search top_k most similar chunks.

        Args:
            query_vector: Embedding vector of user query.
            top_k: Number of retrieved chunks.

        Returns:
            A list of retrieved chunk dictionaries with rank and score.
        """
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")
        
        if not self.chunks or not self.vectors:
            return []
        
        if self.embedding_dimension is None:
            return []
        
        if len(query_vector) != self.embedding_dimension:
            raise ValueError(
                f"query vector dimension mismatch, "
                f"expected {self.embedding_dimension}, got {len(query_vector)}"
            )

        matrix  = np.array(self.vectors,dtype = np.float32)
        query = np.array(query_vector,dtype=np.float32)

        scores = matrix@query

        top_k = min(top_k,len(self.chunks))
        top_indices = np.argsort(scores)[::-1][:top_k]

        results:List[Dict[str,Any]] = []
        
        for rank, idx in enumerate(top_indices,start = 1):
            chunk = self.chunks[int(idx)].copy()
            chunk["rank"] = rank
            chunk["score"] = float(scores[int(idx)])
            results.append(chunk)
        
        return results
    
    def count(self)->int:
        return len(self.chunks)
    
    def clear(self)->None:
        self.chunks = []
        self.vectors = []
        self.embedding_dimension = None