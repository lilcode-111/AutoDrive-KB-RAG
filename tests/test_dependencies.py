import pytest

import app.dependencies as dependencies
from src.llm.fake_llm_client import FakeLLMClient
from src.embeddings.caching_embedding_client import (CachingEmbeddingClient,)


CONFIG_ENV_NAMES = (
    "LLM_PROVIDER",
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "OPENAI_BASE_URL",
    "OPENAI_TIMEOUT",
    "EMBEDDING_MODEL",
    "EMBEDDING_BATCH_SIZE",
    "EMBEDDING_NORMALIZE",
    "DEFAULT_TOP_K",
    "EMBEDDING_CACHE_ENABLED",
    "EMBEDDING_CACHE_MAX_SIZE",
    "LOG_LEVEL",
)


@pytest.fixture(autouse=True)
def reset_dependency_state(
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Reset environment variables and dependency caches around every test.

    Each test must start with a clean dependency container.
    """
    dependencies.clear_dependency_caches()

    for name in CONFIG_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)

    monkeypatch.setenv(
        "LLM_PROVIDER",
        "fake",
    )

    yield

    dependencies.clear_dependency_caches()


def install_stub_embedding_client(
    monkeypatch: pytest.MonkeyPatch,
) -> list[object]:
    """
    Replace the real SentenceTransformer client with a lightweight stub.

    Return a list containing every created stub instance.
    """
    created_instances: list[object] = []

    class StubSentenceTransformerEmbeddingClient:
        def __init__(
            self,
            model_name: str,
            batch_size: int,
            normalize_embeddings: bool,
        ) -> None:
            self.model_name = model_name
            self.batch_size = batch_size
            self.normalize_embeddings = normalize_embeddings

            created_instances.append(self)

    monkeypatch.setattr(
        dependencies,
        "SentenceTransformerEmbeddingClient",
        StubSentenceTransformerEmbeddingClient,
    )

    return created_instances


def test_get_embedding_client_is_lazy_cached_and_wrapped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created_instances = install_stub_embedding_client(
        monkeypatch,
    )

    monkeypatch.setenv(
        "EMBEDDING_MODEL",
        "test-embedding-model",
    )
    monkeypatch.setenv(
        "EMBEDDING_BATCH_SIZE",
        "16",
    )
    monkeypatch.setenv(
        "EMBEDDING_NORMALIZE",
        "false",
    )
    monkeypatch.setenv(
        "EMBEDDING_CACHE_ENABLED",
        "true",
    )
    monkeypatch.setenv(
        "EMBEDDING_CACHE_MAX_SIZE",
        "64",
    )

    # Merely installing the stub must not create the client.
    assert created_instances == []

    first_client = dependencies.get_embedding_client()
    second_client = dependencies.get_embedding_client()

    # The dependency factory itself is cached.
    assert first_client is second_client

    # The real embedding implementation is created only once.
    assert len(created_instances) == 1

    # Cache is enabled, so the returned object is the wrapper.
    assert isinstance(
        first_client,
        CachingEmbeddingClient,
    )
    assert first_client.max_size == 64

    base_client = created_instances[0]

    # The wrapper delegates actual embedding calculation to the base client.
    assert first_client.delegate is base_client

    assert getattr(
        base_client,
        "model_name",
    ) == "test-embedding-model"

    assert getattr(
        base_client,
        "batch_size",
    ) == 16

    assert getattr(
        base_client,
        "normalize_embeddings",
    ) is False


def test_get_retrieval_service_is_cached(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_stub_embedding_client(
        monkeypatch,
    )

    first_service = dependencies.get_retrieval_service()
    second_service = dependencies.get_retrieval_service()

    assert first_service is second_service

    assert (
        first_service.embedding_client
        is dependencies.get_embedding_client()
    )

    assert (
        first_service.vector_index
        is second_service.vector_index
    )


def test_get_llm_client_returns_cached_fake_client() -> None:
    first_client = dependencies.get_llm_client()
    second_client = dependencies.get_llm_client()

    assert first_client is second_client
    assert isinstance(
        first_client,
        FakeLLMClient,
    )
    assert first_client.response == dependencies.FAKE_LLM_RESPONSE


def test_get_llm_client_builds_openai_client_from_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created_instances: list[object] = []

    class StubOpenAICompatibleLLMClient:
        def __init__(
            self,
            api_key: str,
            model: str,
            base_url: str,
            timeout: float,
        ) -> None:
            self.api_key = api_key
            self.model = model
            self.base_url = base_url
            self.timeout = timeout

            created_instances.append(self)

    monkeypatch.setattr(
        dependencies,
        "OpenAICompatibleLLMClient",
        StubOpenAICompatibleLLMClient,
    )

    monkeypatch.setenv(
        "LLM_PROVIDER",
        "openai",
    )
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-api-key",
    )
    monkeypatch.setenv(
        "OPENAI_MODEL",
        "test-model",
    )
    monkeypatch.setenv(
        "OPENAI_BASE_URL",
        "https://example.test/v1",
    )
    monkeypatch.setenv(
        "OPENAI_TIMEOUT",
        "30",
    )

    first_client = dependencies.get_llm_client()
    second_client = dependencies.get_llm_client()

    assert first_client is second_client
    assert len(created_instances) == 1

    assert first_client.api_key == "test-api-key"
    assert first_client.model == "test-model"
    assert first_client.base_url == "https://example.test/v1"
    assert first_client.timeout == 30.0


def test_get_rag_service_reuses_shared_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_stub_embedding_client(
        monkeypatch,
    )

    retrieval_service = dependencies.get_retrieval_service()
    llm_client = dependencies.get_llm_client()

    first_rag_service = dependencies.get_rag_service()
    second_rag_service = dependencies.get_rag_service()

    assert first_rag_service is second_rag_service

    assert (
        first_rag_service.retrieval_service
        is retrieval_service
    )

    assert first_rag_service.llm_client is llm_client


def test_clear_dependency_caches_removes_cached_instances(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_stub_embedding_client(
        monkeypatch,
    )

    dependencies.get_rag_service()

    assert dependencies.get_settings.cache_info().currsize == 1
    assert (
        dependencies.get_embedding_client.cache_info().currsize
        == 1
    )
    assert (
        dependencies.get_retrieval_service.cache_info().currsize
        == 1
    )
    assert (
        dependencies.get_llm_client.cache_info().currsize
        == 1
    )
    assert (
        dependencies.get_rag_service.cache_info().currsize
        == 1
    )

    dependencies.clear_dependency_caches()

    assert dependencies.get_settings.cache_info().currsize == 0
    assert (
        dependencies.get_embedding_client.cache_info().currsize
        == 0
    )
    assert (
        dependencies.get_retrieval_service.cache_info().currsize
        == 0
    )
    assert (
        dependencies.get_llm_client.cache_info().currsize
        == 0
    )
    assert (
        dependencies.get_rag_service.cache_info().currsize
        == 0
    )

def test_get_embedding_client_returns_base_client_when_cache_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created_instances = install_stub_embedding_client(
        monkeypatch,
    )

    monkeypatch.setenv(
        "EMBEDDING_CACHE_ENABLED",
        "false",
    )

    client = dependencies.get_embedding_client()

    assert len(created_instances) == 1

    base_client = created_instances[0]

    assert client is base_client
    assert not isinstance(
        client,
        CachingEmbeddingClient,
    )