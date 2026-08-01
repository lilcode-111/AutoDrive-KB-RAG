import logging

from app.main import app
from app.config import get_settings


def test_application_import_configures_logging() -> None:
    settings = get_settings()

    root_logger = logging.getLogger()

    assert root_logger.level == getattr(
        logging,
        settings.log_level,
    )