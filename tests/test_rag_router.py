from typing import Any, Dict

import pytest
from fastapi import HTTPException

from app.routers import rag as rag_router


class StubRAGService:
    """
    Stub service used to test the API layer without running retrieval or LLM.
    """

    def answer(
        self,
        query: str,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        return {
            "query": query,
            "answer": "FN 表示真实目标存在，但系统没有检测到该目标。[S1]",
            "answer_status": "answered",
            "source_count": 1,
            "sources": [
                {
                    "rank": 1,
                    "score": 0.95,
                    "chunk_id": "metric_fn",
                    "source": "metric_doc.md",
                    "doc_type": "markdown",
                    "text": "FN 表示真实目标存在，但系统没有检测到该目标。",
                    "text_length": 27,
                    "metadata": {
                        "metric_name": "FN",
                    },
                }
            ],
        }


class InvalidRequestStubRAGService:
    """
    Stub service that simulates a business validation error.
    """

    def answer(
        self,
        query: str,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        raise ValueError("query must not be blank")


def test_rag_answer_route_is_registered() -> None:
    route_paths = {
        route.path
        for route in rag_router.router.routes
    }

    assert "/api/v1/rag/answer" in route_paths


def test_answer_question_returns_rag_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        rag_router,
        "rag_service",
        StubRAGService(),
    )

    request = rag_router.RAGAnswerRequest(
        query="什么是 FN？",
        top_k=1,
    )

    response = rag_router.answer_question(request)

    assert response.query == "什么是 FN？"
    assert response.answer_status == "answered"
    assert response.source_count == 1
    assert len(response.sources) == 1
    assert response.sources[0].chunk_id == "metric_fn"
    assert response.sources[0].source == "metric_doc.md"


def test_answer_question_converts_validation_error_to_http_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        rag_router,
        "rag_service",
        InvalidRequestStubRAGService(),
    )

    request = rag_router.RAGAnswerRequest(
        query="   ",
        top_k=1,
    )

    with pytest.raises(HTTPException) as exc_info:
        rag_router.answer_question(request)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "query must not be blank"