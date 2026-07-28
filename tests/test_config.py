import pytest

from app.config import (
    DEFAULT_EMBEDDING_MODEL,
    Settings,
    get_settings,
)


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """
    Clear the cached Settings object before and after every test.

    This prevents one test's environment configuration from affecting
    another test.
    """
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_settings_use_expected_defaults() -> None:
    settings = Settings.from_env({})

    assert settings.llm_provider == "fake"

    assert settings.openai_api_key is None
    assert settings.openai_model is None
    assert settings.openai_base_url is None
    assert settings.openai_timeout == 60.0

    assert settings.embedding_model == DEFAULT_EMBEDDING_MODEL
    assert settings.embedding_batch_size == 32
    assert settings.embedding_normalize is True

    assert settings.default_top_k == 5

    assert settings.embedding_cache_enabled is True
    assert settings.embedding_cache_max_size == 1024

    assert settings.log_level == "INFO"


def test_settings_read_environment_overrides() -> None:
    settings = Settings.from_env(
        {
            "LLM_PROVIDER": "openai",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_MODEL": "test-model",
            "OPENAI_BASE_URL": "https://example.test/v1",
            "OPENAI_TIMEOUT": "30",
            "EMBEDDING_MODEL": "test-embedding-model",
            "EMBEDDING_BATCH_SIZE": "16",
            "EMBEDDING_NORMALIZE": "false",
            "DEFAULT_TOP_K": "3",
            "EMBEDDING_CACHE_ENABLED": "false",
            "EMBEDDING_CACHE_MAX_SIZE": "128",
            "LOG_LEVEL": "debug",
        }
    )

    assert settings.llm_provider == "openai"

    assert settings.openai_api_key == "test-key"
    assert settings.openai_model == "test-model"
    assert settings.openai_base_url == "https://example.test/v1"
    assert settings.openai_timeout == 30.0

    assert settings.embedding_model == "test-embedding-model"
    assert settings.embedding_batch_size == 16
    assert settings.embedding_normalize is False

    assert settings.default_top_k == 3

    assert settings.embedding_cache_enabled is False
    assert settings.embedding_cache_max_size == 128

    assert settings.log_level == "DEBUG"


def test_settings_strip_string_values() -> None:
    settings = Settings.from_env(
        {
            "LLM_PROVIDER": "  FAKE  ",
            "EMBEDDING_MODEL": "  test-model  ",
            "LOG_LEVEL": "  warning  ",
        }
    )

    assert settings.llm_provider == "fake"
    assert settings.embedding_model == "test-model"
    assert settings.log_level == "WARNING"


def test_openai_provider_requires_api_key_and_model() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Missing required configuration for openai provider: "
            "OPENAI_API_KEY, OPENAI_MODEL"
        ),
    ):
        Settings.from_env(
            {
                "LLM_PROVIDER": "openai",
            }
        )


def test_settings_reject_unknown_llm_provider() -> None:
    with pytest.raises(
        ValueError,
        match="LLM_PROVIDER must be either",
    ):
        Settings.from_env(
            {
                "LLM_PROVIDER": "unknown",
            }
        )


@pytest.mark.parametrize(
    ("name", "value", "expected_message"),
    [
        (
            "OPENAI_TIMEOUT",
            "0",
            "OPENAI_TIMEOUT must be greater than 0",
        ),
        (
            "EMBEDDING_BATCH_SIZE",
            "-1",
            "EMBEDDING_BATCH_SIZE must be greater than 0",
        ),
        (
            "DEFAULT_TOP_K",
            "not-an-integer",
            "DEFAULT_TOP_K must be an integer",
        ),
        (
            "EMBEDDING_CACHE_MAX_SIZE",
            "0",
            "EMBEDDING_CACHE_MAX_SIZE must be greater than 0",
        ),
    ],
)
def test_settings_reject_invalid_numeric_values(
    name: str,
    value: str,
    expected_message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        Settings.from_env(
            {
                name: value,
            }
        )


def test_settings_reject_invalid_boolean_value() -> None:
    with pytest.raises(
        ValueError,
        match="EMBEDDING_NORMALIZE must be one of",
    ):
        Settings.from_env(
            {
                "EMBEDDING_NORMALIZE": "maybe",
            }
        )


def test_settings_reject_invalid_log_level() -> None:
    with pytest.raises(
        ValueError,
        match="LOG_LEVEL must be one of",
    ):
        Settings.from_env(
            {
                "LOG_LEVEL": "verbose",
            }
        )


def test_get_settings_returns_cached_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "fake",
    )

    first_settings = get_settings()
    second_settings = get_settings()

    assert first_settings is second_settings


def test_settings_repr_does_not_expose_api_key() -> None:
    settings = Settings.from_env(
        {
            "LLM_PROVIDER": "openai",
            "OPENAI_API_KEY": "super-secret-key",
            "OPENAI_MODEL": "test-model",
        }
    )

    settings_repr = repr(settings)

    assert "super-secret-key" not in settings_repr
    assert "openai_api_key" not in settings_repr