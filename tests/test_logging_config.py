import io
import logging

import pytest

from app.logging_config import (
    APPLICATION_HANDLER_NAME,
    configure_logging,
)


@pytest.fixture(autouse=True)
def clean_application_logging_handler():
    """
    Remove only the handler created by the application.
    """
    root_logger = logging.getLogger()
    previous_level = root_logger.level

    yield

    for handler in list(root_logger.handlers):
        if (
            handler.get_name()
            == APPLICATION_HANDLER_NAME
        ):
            root_logger.removeHandler(handler)
            handler.close()

    root_logger.setLevel(previous_level)


def test_configure_logging_emits_formatted_message() -> None:
    stream = io.StringIO()

    configure_logging(
        log_level="debug",
        stream=stream,
    )

    logger = logging.getLogger(
        "tests.logging"
    )

    logger.debug(
        "embedding cache hit"
    )

    output = stream.getvalue()

    assert "DEBUG" in output
    assert "tests.logging" in output
    assert "embedding cache hit" in output


def test_configure_logging_respects_log_level() -> None:
    stream = io.StringIO()

    configure_logging(
        log_level="WARNING",
        stream=stream,
    )

    logger = logging.getLogger(
        "tests.logging"
    )

    logger.info(
        "hidden informational message"
    )
    logger.warning(
        "visible warning message"
    )

    output = stream.getvalue()

    assert (
        "hidden informational message"
        not in output
    )

    assert (
        "visible warning message"
        in output
    )


def test_repeated_configuration_does_not_duplicate_handler() -> None:
    stream = io.StringIO()

    configure_logging(
        log_level="INFO",
        stream=stream,
    )

    configure_logging(
        log_level="INFO",
        stream=stream,
    )

    root_logger = logging.getLogger()

    application_handlers = [
        handler
        for handler in root_logger.handlers
        if (
            handler.get_name()
            == APPLICATION_HANDLER_NAME
        )
    ]

    assert len(application_handlers) == 1

    logger = logging.getLogger(
        "tests.logging"
    )

    logger.info(
        "single message"
    )

    assert (
        stream.getvalue().count(
            "single message"
        )
        == 1
    )


@pytest.mark.parametrize(
    "log_level",
    [
        "",
        "TRACE",
        "INVALID",
    ],
)
def test_configure_logging_rejects_invalid_level(
    log_level: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="log_level must be one of",
    ):
        configure_logging(
            log_level=log_level
        )


def test_configure_logging_rejects_non_string_level() -> None:
    with pytest.raises(
        TypeError,
        match="log_level must be a string",
    ):
        configure_logging(
            log_level=10,  # type: ignore[arg-type]
        )