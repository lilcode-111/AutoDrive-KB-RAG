from typing import List

import pytest

from src.embeddings.caching_embedding_client import (
    CachingEmbeddingClient,
)
from src.embeddings.embedding_client import EmbeddingClient


class StubEmbeddingClient(EmbeddingClient):
    """
    Lightweight embedding client used to observe delegate calls.
    """

    def __init__(self) -> None:
        self.text_calls: List[List[str]] = []
        self.query_calls: List[str] = []

    @staticmethod
    def document_vector(text: str) -> List[float]:
        return [
            float(len(text)),
            float(sum(ord(character) for character in text)),
        ]

    @staticmethod
    def query_vector(query: str) -> List[float]:
        return [
            1000.0,
            float(len(query)),
        ]

    def embed_texts(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        self.text_calls.append(list(texts))

        return [
            self.document_vector(text)
            for text in texts
        ]

    def embed_query(
        self,
        query: str,
    ) -> List[float]:
        self.query_calls.append(query)

        return self.query_vector(query)


class InvalidCountEmbeddingClient(EmbeddingClient):
    """
    Delegate that deliberately returns the wrong vector count.
    """

    def embed_texts(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        return []

    def embed_query(
        self,
        query: str,
    ) -> List[float]:
        return [1.0]


def test_constructor_rejects_missing_delegate() -> None:
    with pytest.raises(
        ValueError,
        match="delegate must not be None",
    ):
        CachingEmbeddingClient(
            delegate=None,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "max_size",
    [
        True,
        1.5,
        "10",
    ],
)
def test_constructor_rejects_non_integer_max_size(
    max_size: object,
) -> None:
    delegate = StubEmbeddingClient()

    with pytest.raises(
        TypeError,
        match="max_size must be an integer",
    ):
        CachingEmbeddingClient(
            delegate=delegate,
            max_size=max_size,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "max_size",
    [
        0,
        -1,
    ],
)
def test_constructor_rejects_non_positive_max_size(
    max_size: int,
) -> None:
    delegate = StubEmbeddingClient()

    with pytest.raises(
        ValueError,
        match="max_size must be greater than 0",
    ):
        CachingEmbeddingClient(
            delegate=delegate,
            max_size=max_size,
        )


def test_embed_texts_deduplicates_and_caches_vectors() -> None:
    delegate = StubEmbeddingClient()

    client = CachingEmbeddingClient(
        delegate=delegate,
        max_size=10,
    )

    first_result = client.embed_texts(
        [
            "alpha",
            "beta",
            "alpha",
        ]
    )

    assert delegate.text_calls == [
        [
            "alpha",
            "beta",
        ]
    ]

    assert first_result == [
        delegate.document_vector("alpha"),
        delegate.document_vector("beta"),
        delegate.document_vector("alpha"),
    ]

    assert client.cache_size() == 2

    second_result = client.embed_texts(
        [
            "beta",
            "gamma",
            "alpha",
        ]
    )

    assert delegate.text_calls == [
        [
            "alpha",
            "beta",
        ],
        [
            "gamma",
        ],
    ]

    assert second_result == [
        delegate.document_vector("beta"),
        delegate.document_vector("gamma"),
        delegate.document_vector("alpha"),
    ]

    assert client.cache_size() == 3


def test_embed_query_reuses_cached_vector() -> None:
    delegate = StubEmbeddingClient()

    client = CachingEmbeddingClient(
        delegate=delegate,
        max_size=10,
    )

    first_vector = client.embed_query("什么是 FN？")
    second_vector = client.embed_query("什么是 FN？")

    assert delegate.query_calls == [
        "什么是 FN？",
    ]

    assert first_vector == delegate.query_vector(
        "什么是 FN？"
    )
    assert second_vector == first_vector

    assert second_vector is not first_vector
    assert client.cache_size() == 1


def test_document_and_query_cache_namespaces_are_separate() -> None:
    delegate = StubEmbeddingClient()

    client = CachingEmbeddingClient(
        delegate=delegate,
        max_size=10,
    )

    document_vector = client.embed_texts(
        [
            "same text",
        ]
    )[0]

    query_vector = client.embed_query(
        "same text"
    )

    assert delegate.text_calls == [
        [
            "same text",
        ]
    ]

    assert delegate.query_calls == [
        "same text",
    ]

    assert document_vector == delegate.document_vector(
        "same text"
    )
    assert query_vector == delegate.query_vector(
        "same text"
    )

    assert client.cache_size() == 2


def test_cache_evicts_least_recently_used_entry() -> None:
    delegate = StubEmbeddingClient()

    client = CachingEmbeddingClient(
        delegate=delegate,
        max_size=2,
    )

    client.embed_query("a")
    client.embed_query("b")

    # Access "a" again, making "b" the least recently used entry.
    client.embed_query("a")

    # Adding "c" should evict "b".
    client.embed_query("c")

    # "b" must now be generated again.
    client.embed_query("b")

    assert delegate.query_calls == [
        "a",
        "b",
        "c",
        "b",
    ]

    assert client.cache_size() == 2


def test_returned_vector_cannot_modify_cached_vector() -> None:
    delegate = StubEmbeddingClient()

    client = CachingEmbeddingClient(
        delegate=delegate,
        max_size=10,
    )

    first_vector = client.embed_query(
        "protected"
    )

    expected_vector = list(first_vector)

    first_vector[0] = -999.0

    second_vector = client.embed_query(
        "protected"
    )

    assert second_vector == expected_vector
    assert second_vector[0] != -999.0

    assert delegate.query_calls == [
        "protected",
    ]


def test_clear_cache_removes_all_cached_vectors() -> None:
    delegate = StubEmbeddingClient()

    client = CachingEmbeddingClient(
        delegate=delegate,
        max_size=10,
    )

    client.embed_texts(
        [
            "document",
        ]
    )
    client.embed_query(
        "query"
    )

    assert client.cache_size() == 2

    client.clear_cache()

    assert client.cache_size() == 0

    client.embed_query(
        "query"
    )

    assert delegate.query_calls == [
        "query",
        "query",
    ]


def test_empty_text_list_does_not_call_delegate() -> None:
    delegate = StubEmbeddingClient()

    client = CachingEmbeddingClient(
        delegate=delegate,
        max_size=10,
    )

    result = client.embed_texts([])

    assert result == []
    assert delegate.text_calls == []
    assert client.cache_size() == 0


def test_embed_texts_rejects_unexpected_vector_count() -> None:
    client = CachingEmbeddingClient(
        delegate=InvalidCountEmbeddingClient(),
        max_size=10,
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "Embedding client returned an unexpected "
            "number of vectors"
        ),
    ):
        client.embed_texts(
            [
                "alpha",
            ]
        )