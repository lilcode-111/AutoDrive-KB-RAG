from __future__ import annotations

from collections import OrderedDict
from threading import RLock
from typing import List, Optional, Tuple

from src.embeddings.embedding_client import EmbeddingClient

CacheKey = Tuple[str,str]

class CachingEmbeddingClient(EmbeddingClient):
    """
    In-process LRU cache wrapper for an EmbeddingClient.

    Document embeddings and query embeddings use different cache-key
    namespaces so that asymmetric embedding implementations remain safe.
    """

    def __init__(self, delegate: EmbeddingClient, max_size: int = 1024) -> None:
        if delegate is None:
            raise ValueError("delegate must not be None")
        
        if isinstance(max_size, bool) or not isinstance(max_size, int):
            raise TypeError("max_size must be an integer")
        
        if max_size <= 0:
            raise ValueError("max_size must be greater than 0")
        
        self.delegate = delegate
        self.max_size = max_size

        self._cache: OrderedDict[CacheKey, List[float]] = OrderedDict()

        self._lock = RLock()

    @staticmethod
    def _normalize_text(text: str | None)-> str:
        """
        Normalize input consistently with the current embedding client.
        """
        if text is None:
            return ""
        
        return str(text)
    
    def _get_cached(self, key: CacheKey,) -> Optional[List[float]]:
        """
        Return a copied cached vector and mark it as recently used.
        """
        with self._lock:
            vector = self._cache.get(key)
        
            if vector is None:
                return None
            
            self._cache.move_to_end(key)
        
            return list(vector)

    def _store_cached(self, key:CacheKey, vector: List[float]) -> None:
        """
        Store a copied vector and evict the least recently used item.
        """
        with self._lock:
            self._cache[key] = list(vector)
            self._cache.move_to_end(key)

            while len(self._cache) > self.max_size:
                self._cache.popitem(last=False)
    
    def embed_texts(self, texts: List[str],) -> List[List[float]]:
        """
        Embed document texts while reusing cached vectors.

        Only unique cache misses are sent to the wrapped client.
        The returned vectors preserve the original input order.
        """
        if not texts:
            return []
        
        normalized_texts = [self._normalize_text(text) for text in texts]

        resolved_vectors: dict[CacheKey, List[float]] = {}

        missing_texts: List[str] = []
        missing_keys: set[CacheKey] = set()

        for text in normalized_texts:
            key = ("document",text)
            cached_vector = self._get_cached(key)

            if cached_vector is not None:
                resolved_vectors[key] = cached_vector
                continue
            
            if key not in missing_keys:
                missing_keys.add(key)
                missing_texts.append(text)

        if missing_texts:
            generated_vectors = self.delegate.embed_texts(
                missing_texts
            )
            
            if len(generated_vectors) != len(missing_texts):
                raise RuntimeError(
                    "Embedding client returned an unexpected "
                    "number of vectors"
                )

            for text, vector in zip(missing_texts, generated_vectors,):
                key = ("document", text)
                vector_copy = list(vector)
                self._store_cached(key, vector_copy)
                resolved_vectors[key] = vector_copy
            
        return [list(resolved_vectors[("document",text)]) for text in normalized_texts]
    

    def embed_query(self, query:str)->List[float]:
        """
        Embed a query while reusing a cached query vector.
        """
        normalized_query = self._normalize_text(query)

        key = ("query", normalized_query)
        
        cached_vector = self._get_cached(key)

        if cached_vector is not None:
            return cached_vector
        
        generated_vector = self.delegate.embed_query(normalized_query)

        vector_copy = list(generated_vector)

        self._store_cached(key, vector_copy)

        return list(vector_copy)
    
    def get_embedding_dimension(self) -> int:
        """
        Delegate embedding-dimension discovery to the wrapped client.
        """
        return self.delegate.get_embedding_dimension()
    
    def clear_cache(self) -> None:
        """
        Remove all cached embedding vectors.
        """
        with self._lock:
            self._cache.clear()

    def cache_size(self) -> int:
        """
        Return the current number of cached vectors.
        """
        with self._lock:
            return len(self._cache)

