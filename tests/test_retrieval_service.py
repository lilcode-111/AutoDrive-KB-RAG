from typing import List

import pytest

from src.embeddings.embedding_client import EmbeddingClient
from src.retrieval.retrieval_service import RetrievalService
from src.retrieval.vector_index import InMemoryVectorIndex


class FakeEmbeddingClient(EmbeddingClient):
    """
    A deterministic embedding client used only for unit tests.

    It avoids loading the real SentenceTransformer model,
    so tests run quickly and do not require network access.
    """

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, query: str) -> List[float]:
        return self._embed(query)

    def _embed(self, text: str) -> List[float]:
        normalized_text = str(text).lower()

        if "fn" in normalized_text or "漏检" in normalized_text:
            return [1.0, 0.0, 0.0]

        if "fp" in normalized_text or "误检" in normalized_text:
            return [0.0, 1.0, 0.0]

        return [0.0, 0.0, 1.0]


def build_retrieval_service() -> RetrievalService:
    return RetrievalService(
        embedding_client=FakeEmbeddingClient(),
        vector_index=InMemoryVectorIndex(),
    )


def test_index_chunks() -> None:
    service = build_retrieval_service()

    chunks = [
        {
            "chunk_id": "chunk_fn",
            "text": "FN 表示漏检。",
        },
        {
            "chunk_id": "chunk_fp",
            "text": "FP 表示误检。",
        },
    ]

    result = service.index_chunks(chunks)

    assert result["status"] == "success"
    assert result["indexed_chunk_count"] == 2
    assert result["total_indexed_chunk_count"] == 2
    assert result["embedding_dimension"] == 3
    assert service.count() == 2


def test_search_returns_fn_chunk_first() -> None:
    service = build_retrieval_service()

    chunks = [
        {
            "chunk_id": "chunk_fp",
            "text": "FP 表示系统检测到了不存在的目标。",
        },
        {
            "chunk_id": "chunk_fn",
            "text": "FN 表示真实目标没有被检测出来，也就是漏检。",
        },
        {
            "chunk_id": "chunk_recall",
            "text": "Recall 用于衡量真实目标被成功检测的比例。",
        },
    ]

    service.index_chunks(chunks)

    result = service.search(
        query="什么是 FN 漏检？",
        top_k=2,
    )

    assert result["result_count"] == 2
    assert result["results"][0]["chunk_id"] == "chunk_fn"
    assert result["results"][0]["rank"] == 1
    assert result["results"][0]["score"] == pytest.approx(1.0)


def test_clear_index() -> None:
    service = build_retrieval_service()

    service.index_chunks(
        [
            {
                "chunk_id": "chunk_fn",
                "text": "FN 表示漏检。",
            }
        ]
    )

    assert service.count() == 1

    service.clear()

    assert service.count() == 0


def test_empty_query_raises_error() -> None:
    service = build_retrieval_service()

    with pytest.raises(ValueError):
        service.search(
            query="",
            top_k=3,
        )