from typing import List

import pytest

from src.embeddings.embedding_client import EmbeddingClient
from src.llm.fake_llm_client import FakeLLMClient
from src.rag.rag_service import (
    INSUFFICIENT_CONTEXT_ANSWER,
    RAGService,
)
from src.retrieval.retrieval_service import RetrievalService
from src.retrieval.vector_index import InMemoryVectorIndex


class FakeEmbeddingClient(EmbeddingClient):
    """
    Deterministic embedding client used for RAGService tests.

    It avoids loading the real SentenceTransformer model.
    """

    def embed_texts(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(
        self,
        query: str,
    ) -> List[float]:
        return self._embed(query)

    def _embed(
        self,
        text: str,
    ) -> List[float]:
        normalized_text = str(text).lower()

        if "scenario_001" in normalized_text:
            return [1.0, 0.0, 0.0]

        if "fn" in normalized_text or "漏检" in normalized_text:
            return [0.8, 0.2, 0.0]

        if "fp" in normalized_text or "误检" in normalized_text:
            return [0.0, 1.0, 0.0]

        return [0.0, 0.0, 1.0]


def build_retrieval_service() -> RetrievalService:
    return RetrievalService(
        embedding_client=FakeEmbeddingClient(),
        vector_index=InMemoryVectorIndex(),
    )


def test_rag_service_connects_retrieval_prompt_and_llm() -> None:
    retrieval_service = build_retrieval_service()

    retrieval_service.index_chunks(
        [
            {
                "chunk_id": "scenario_001",
                "source": "evaluation_result.json",
                "doc_type": "json",
                "text": (
                    "scenario_001 中真实标签包含一名行人，"
                    "但检测结果中没有对应行人目标。"
                ),
                "metadata": {
                    "scenario_id": "scenario_001",
                    "failure_type": "FN",
                },
            },
            {
                "chunk_id": "metric_fn",
                "source": "metric_doc.md",
                "doc_type": "markdown",
                "text": (
                    "FN 表示真实目标存在，"
                    "但检测系统没有检测到该目标。"
                ),
                "metadata": {
                    "metric_name": "FN",
                },
            },
        ]
    )

    llm_client = FakeLLMClient(
        response=(
            "scenario_001 被判定为 FN，"
            "因为真实行人存在，但系统没有检测到该目标。[S1][S2]"
        )
    )

    rag_service = RAGService(
        retrieval_service=retrieval_service,
        llm_client=llm_client,
    )

    result = rag_service.answer(
        query="scenario_001 为什么被判定为 FN？",
        top_k=2,
    )

    assert result["query"] == "scenario_001 为什么被判定为 FN？"
    assert result["answer_status"] == "answered"
    assert result["source_count"] == 2
    assert len(result["sources"]) == 2

    assert "scenario_001 被判定为 FN" in result["answer"]

    assert llm_client.call_count == 1
    assert llm_client.last_prompt is not None
    assert "scenario_001 为什么被判定为 FN？" in llm_client.last_prompt
    assert "真实标签包含一名行人" in llm_client.last_prompt
    assert "FN 表示真实目标存在" in llm_client.last_prompt


def test_rag_service_does_not_call_llm_without_context() -> None:
    retrieval_service = build_retrieval_service()
    llm_client = FakeLLMClient(response="不应该返回这条答案")

    rag_service = RAGService(
        retrieval_service=retrieval_service,
        llm_client=llm_client,
    )

    result = rag_service.answer(
        query="知识库中不存在的问题",
        top_k=3,
    )

    assert result == {
        "query": "知识库中不存在的问题",
        "answer": INSUFFICIENT_CONTEXT_ANSWER,
        "answer_status": "insufficient_context",
        "source_count": 0,
        "sources": [],
    }

    assert llm_client.call_count == 0
    assert llm_client.last_prompt is None


@pytest.mark.parametrize(
    "invalid_query",
    [
        "",
        "   ",
        "\n\t",
    ],
)
def test_rag_service_rejects_blank_query(
    invalid_query: str,
) -> None:
    rag_service = RAGService(
        retrieval_service=build_retrieval_service(),
        llm_client=FakeLLMClient(response="测试答案"),
    )

    with pytest.raises(
        ValueError,
        match="query must not be blank",
    ):
        rag_service.answer(
            query=invalid_query,
            top_k=3,
        )


@pytest.mark.parametrize(
    "invalid_top_k",
    [
        0,
        -1,
    ],
)
def test_rag_service_rejects_invalid_top_k(
    invalid_top_k: int,
) -> None:
    rag_service = RAGService(
        retrieval_service=build_retrieval_service(),
        llm_client=FakeLLMClient(response="测试答案"),
    )

    with pytest.raises(
        ValueError,
        match="top_k must be greater than 0",
    ):
        rag_service.answer(
            query="什么是 FN？",
            top_k=invalid_top_k,
        )