from __future__ import annotations
import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Mapping


DEFAULT_EMBEDDING_MODEL = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

VALID_LLM_PROVIDERS = {"fake", "openai"}

VALID_LOG_LEVELS = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}

TRUE_VALUES = {"1","true","yes","on"}
FALSE_VALUES = {"0","false","no","off"}

def _read_optional_string(
        environ: Mapping[str,str],
        name: str,
        default: str| None = None,
) -> str|None:
    """
    Read an optional string environment variable.

    Missing or blank values are treated as the supplied default.
    """
    raw_value = environ.get(name)

    if raw_value is None:
        return default
    
    cleaned_value = raw_value.strip()

    if not cleaned_value:
        return default
    
    return cleaned_value

def _read_positive_int(
        environ: Mapping[str,str],
        name: str,
        default: int,
) -> int:
    """
    Read a positive integer environment variable.
    """
    raw_value = _read_optional_string(environ, name)

    if raw_value is None:
        return default
    
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(
            f"{name} must be an integer"
        ) from exc

    if value <= 0:
        raise ValueError(
            f"{name} must be greater than 0"
        )
    
    return value

def _read_positive_float(
        environ: Mapping[str,str],
        name: str,
        default: float,
) -> float:
    """
    Read a positive floating-point environment variable.
    """
    raw_value = _read_optional_string(environ, name)

    if raw_value is None:
        return default
    
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ValueError(
            f"{name} must be a number"
        ) from exc
    
    if value <= 0:
        raise ValueError(
            f"{name} must be greater than 0"
        )
    
    return value

def _read_bool(
        environ: Mapping[str,str],
        name: str,
        default: bool,
) -> bool:
    """
    Read a boolean environment variable.
    """
    raw_value = _read_optional_string(environ, name)

    if raw_value is None:
        return default
    
    normalized_value = raw_value.lower()

    if normalized_value in TRUE_VALUES:
        return True
    
    if normalized_value in FALSE_VALUES:
        return False
    
    raise ValueError(
        f"{name} must be one of: "
        "true, false, 1, 0, yes, no, on, off"
    )

@dataclass(frozen=True)
class Settings:
    """
    Central application configuration.

    Configuration values are loaded from environment variables by from_env().
    """
    app_name: str = "AutoDrive-KB-RAG"
    version: str = "0.1.0"

    llm_provider : str = "fake"

    openai_api_key: str | None = field(
        default=None,
        repr = False
    )

    openai_model: str | None = None
    openai_base_url: str| None = None
    openai_timeout: float = 60.0

    embedding_model: str = DEFAULT_EMBEDDING_MODEL
    embedding_batch_size: int = 32
    embedding_normalize: bool = True

    default_top_k: int = 5

    embedding_cache_enabled: bool = True
    embedding_cache_max_size: int = 1024

    log_level: str = "INFO"

    @classmethod
    def from_env(
        cls,
        environ: Mapping[str,str] | None = None
    ) -> "Settings":
        """
        Build application settings from environment variables.

        A custom mapping can be passed during unit tests.
        """
        source = os.environ if environ is None else environ

        llm_provider = (
            _read_optional_string(
                source,
                "LLM_PROVIDER",
                "fake",
            )
            or "fake"
        ).lower()

        if llm_provider not in VALID_LLM_PROVIDERS:
            raise ValueError(
                "LLM_PROVIDER must be either "
                "'fake' or 'openai'"
            )

        openai_api_key = _read_optional_string(
            source,
            "OPENAI_API_KEY",
        )

        openai_model = _read_optional_string(
            source,
            "OPENAI_MODEL",
        )

        openai_base_url = _read_optional_string(
            source,
            "OPENAI_BASE_URL",
        )

        if llm_provider == "openai":
            missing_names: list[str] = []

            if openai_api_key is None:
                missing_names.append("OPENAI_API_KEY")

            if openai_model is None:
                missing_names.append("OPENAI_MODEL")
            
            if missing_names:
                raise ValueError(
                    "Missing required configuration for "
                    "openai provider: "
                    + ", ".join(missing_names)
                )
        
        embedding_model = (
            _read_optional_string(
                source,
                "EMBEDDING_MODEL",
                DEFAULT_EMBEDDING_MODEL,
            )
            or DEFAULT_EMBEDDING_MODEL
        )

        log_level = (
            _read_optional_string(
                source,
                "LOG_LEVEL",
                "INFO",
            )
            or "INFO"
        ).upper()

        if log_level not in VALID_LOG_LEVELS:
            raise ValueError(
                "LOG_LEVEL must be one of: "
                "DEBUG, INFO, WARNING, ERROR, CRITICAL"
            )
        
        return cls(
            llm_provider=llm_provider,
            openai_api_key=openai_api_key,
            openai_model=openai_model,
            openai_base_url=openai_base_url,
            openai_timeout=_read_positive_float(
                source,
                "OPENAI_TIMEOUT",
                60.0,
            ),
            embedding_model=embedding_model,
            embedding_batch_size=_read_positive_int(
                source,
                "EMBEDDING_BATCH_SIZE",
                32,
            ),
            embedding_normalize=_read_bool(
                source,
                "EMBEDDING_NORMALIZE",
                True,
            ),
            default_top_k=_read_positive_int(
                source,
                "DEFAULT_TOP_K",
                5,
            ),
            embedding_cache_enabled=_read_bool(
                source,
                "EMBEDDING_CACHE_ENABLED",
                True,
            ),
            embedding_cache_max_size=_read_positive_int(
                source,
                "EMBEDDING_CACHE_MAX_SIZE",
                1024,
            ),
            log_level=log_level,
        )
    
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the shared Settings instance for the current process.

    Tests that modify environment variables should call:
        get_settings.cache_clear()
    """
    return Settings.from_env()