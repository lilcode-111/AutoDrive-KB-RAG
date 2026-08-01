import logging
from typing import Any,Dict,List,Optional

from src.embeddings.embedding_client import EmbeddingClient
from src.embeddings.sentence_transformer_client import SentenceTransformerEmbeddingClient
from src.retrieval.vector_index import InMemoryVectorIndex

logger = logging.getLogger(__name__)

class RetrievalService:
    """
    Service layer for Week11 retrieval.

    RetrievalService connects:
    1. EmbeddingClient
    2. InMemoryVectorIndex

    It provides two main operations:
    1. index_chunks(): chunks -> embeddings -> vector index
    2. search(): query -> query embedding -> top_k chunks
    """

    def __init__(self,
                 embedding_client:Optional[EmbeddingClient] = None,
                 vector_index: Optional[InMemoryVectorIndex] = None) -> None:
        self.embedding_client = embedding_client or SentenceTransformerEmbeddingClient()
        self.vector_index = vector_index or InMemoryVectorIndex()

    def index_chunks(self,chunks:List[Dict[str,Any]]) -> Dict[str,Any]:
        """
        Index chunks into the vector index.

        Args:
            chunks: List of chunk dictionaries. Each chunk must contain a "text" field.

        Returns:
            A status dictionary with indexing statistics.
        """
        if not chunks:

            logger.info("index_chunks called with empty chunks")

            return {
                "status": "success",
                "indexed_chunk_count": 0,
                "total_indexed_chunk_count": self.vector_index.count(),
                "message": "No chunks to index.",
            }
        
        logger.info("indexing chunks count=%d", len(chunks))

        texts:List[str] = []

        for idx,chunk in enumerate(chunks):
            text = chunk.get("text")

            if text is None or not str(text).strip():
                raise ValueError(f"chunk at index {idx} must contain a non-empty text field")
            
            texts.append(str(text))
        
        vectors = self.embedding_client.embed_texts(texts)
        logger.debug(
            "generated embeddings count=%d dimension=%d",
            len(vectors),
            len(vectors[0]) if vectors else 0,
        )

        self.vector_index.add_chunks(chunks=chunks,vectors=vectors)
        logger.info(
            "chunks indexed successfully total_count=%d",
            self.vector_index.count(),
        )

        return {
            "status": "success",
            "indexed_chunk_count": len(chunks),
            "total_indexed_chunk_count": self.vector_index.count(),
            "embedding_dimension": self.vector_index.embedding_dimension,
        }
    
    def search(self,query:str,top_k: int =5)->Dict[str,Any]:
        """
        Search top_k chunks by semantic similarity.

        Args:
            query: User query.
            top_k: Number of retrieved chunks.

        Returns:
            A dictionary containing query, top_k, result_count, and results.
        """
        if query is None or not str(query).strip():
            raise ValueError("query must be a non-empty string")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")
        
        logger.info("retrieval search query=%s top_k=%d", len(query), top_k)
        
        query_vector = self.embedding_client.embed_query(query)
        results = self.vector_index.search(query_vector=query_vector,top_k=top_k)
        logger.info(
            "retrieval completed result_count=%d",
            len(results),
        )

        return {
            "query": query,
            "top_k": top_k,
            "result_count": len(results),
            "results": results,
        }
    
    def count(self) -> int:
        """
        Return current indexed chunk count.
        """
        return self.vector_index.count()
    
    def clear(self)->None:
        """
        Clear all indexed chunks and vectors.
        """
        previous_count = self.vector_index.count()
        self.vector_index.clear()

        logger.info(
            "retrieval index cleared previous_count=%d",
            previous_count,
        )