import logging

from src.rag.rag_service import RAGService


class StubRetrievalService:

    def search(
        self,
        query: str,
        top_k: int = 5,
    ):
        return {
            "results": [
                {
                    "text": "FN means false negative",
                }
            ]
        }


class StubLLMClient:

    def generate(
        self,
        prompt: str,
    ):
        return "test answer"



def test_rag_service_emits_logs(
    caplog,
):

    service = RAGService(
        retrieval_service=StubRetrievalService(),
        llm_client=StubLLMClient(),
    )

    with caplog.at_level(logging.INFO):

        result = service.answer(
            query="what is FN?",
            top_k=3,
        )


    assert result["answer_status"] == "answered"

    assert (
        "rag answer request"
        in caplog.text
    )

    assert (
        "rag retrieval completed"
        in caplog.text
    )

    assert (
        "calling llm generation"
        in caplog.text
    )

    assert (
        "rag answer generated"
        in caplog.text
    )

class EmptyRetrievalService:

    def search(
        self,
        query: str,
        top_k: int = 5,
    ):
        return {
            "results": []
        }



def test_rag_service_logs_warning_without_context(
    caplog,
):

    service = RAGService(
        retrieval_service=EmptyRetrievalService(),
        llm_client=StubLLMClient(),
    )

    with caplog.at_level(logging.WARNING):

        result = service.answer(
            query="unknown",
        )


    assert (
        result["answer_status"]
        ==
        "insufficient_context"
    )

    assert (
        "no context was retrieved"
        in caplog.text
    )