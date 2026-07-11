from abc import ABC,abstractmethod
from typing import List

class EmbeddingClient(ABC):
    """
    Base interface for embedding clients.

    Week11 uses this abstraction so the retrieval pipeline does not depend
    directly on a specific embedding backend. Later we can switch from
    sentence-transformers to OpenAI embeddings, bge, e5, or a local service
    without changing retrieval/index code.
    """

    @abstractmethod
    def embed_texts(self,texts:List[str])->List[List[float]]:
        """
        Convert a list of texts into embedding vectors.

        Args:
            texts: List of chunk texts or document passages.

        Returns:
            A list of dense vectors. The output length should match len(texts).
        """
        raise NotImplementedError
    
    @abstractmethod
    def embed_query(self,query:str)->List[float]:
        """
        Convert a user query into one embedding vector.

        Args:
            query: User search query.

        Returns:
            One dense vector.
        """
        raise NotImplemented
    
    
