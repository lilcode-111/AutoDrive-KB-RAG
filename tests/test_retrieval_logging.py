import logging

from src.retrieval.retrieval_service import RetrievalService


class StubEmbeddingClient:
    def embed_texts(self, texts):
        return [[1.0, 0.0] for _ in texts]

    def embed_query(self, query):
        return [1.0, 0.0]


def test_index_chunks_emits_log(
    caplog,
):
    service = RetrievalService(
        embedding_client=StubEmbeddingClient(),
    )

    with caplog.at_level(logging.INFO):
        service.index_chunks(
            [
                {
                    "text": "hello",
                }
            ]
        )

    assert (
        "indexing chunks count=1"
        in caplog.text
    )