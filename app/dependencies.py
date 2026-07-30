from functools import lru_cache
from app.config import get_settings
from src.embeddings.embedding_client import EmbeddingClient
from src.embeddings.sentence_transformer_client import (SentenceTransformerEmbeddingClient,)
from src.llm.fake_llm_client import FakeLLMClient
from src.llm.llm_client import LLMClient
from src.llm.openai_compatible_llm_client import (OpenAICompatibleLLMClient,)
from src.rag.rag_service import RAGService
from src.retrieval.retrieval_service import RetrievalService
from src.retrieval.vector_index import InMemoryVectorIndex
from src.embeddings.caching_embedding_client import (CachingEmbeddingClient,)

FAKE_LLM_RESPONSE = "这是一个用于验证 RAG API 链路的测试答案。"

@lru_cache(maxsize=1)
def get_embedding_client()->EmbeddingClient:
    """
    Create and cache the shared embedding client.

    The underlying SentenceTransformer model is created lazily.
    When enabled, embedding results are stored in an in-process LRU cache.
    """
    settings = get_settings()

    base_client: EmbeddingClient = (
        SentenceTransformerEmbeddingClient(
            model_name = settings.embedding_model,
            batch_size = settings.embedding_batch_size,
            normalize_embeddings = settings.embedding_normalize
        )
    )

    if not settings.embedding_cache_enabled:
        return base_client
    
    return CachingEmbeddingClient(
        delegate =  base_client,
        max_size = settings.embedding_cache_max_size, 
    )

@lru_cache(maxsize=1)
def get_retrieval_service() -> RetrievalService:
    """
    Create and cache the shared retrieval service and vector index.
    """
    return RetrievalService(
        embedding_client=get_embedding_client(),
        vector_index=InMemoryVectorIndex(),
    )

@lru_cache(maxsize=1)
def get_llm_client() -> LLMClient:
    """
    Create and cache the configured LLM client.
    """
    settings = get_settings()

    if settings.llm_provider == "fake":
        return FakeLLMClient(
            response=FAKE_LLM_RESPONSE,
        )
    
    return OpenAICompatibleLLMClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        base_url=settings.openai_base_url,
        timeout=settings.openai_timeout,
    )

@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    """
    Create and cache the RAG service.

    The RAG service reuses the same RetrievalService instance used by
    the retrieval API.
    """
    return RAGService(
        retrieval_service=get_retrieval_service(),
        llm_client=get_llm_client(),
    )

def clear_dependency_caches() -> None:
    """
    Clear cached dependency instances.

    Intended for unit tests and controlled application reset.
    """
    get_rag_service.cache_clear()
    get_llm_client.cache_clear()
    get_retrieval_service.cache_clear()
    get_embedding_client.cache_clear()
    get_settings.cache_clear()