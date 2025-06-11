import logging
from logs import logger as logger_module


def test_logger_is_singleton():
    """
    Ensure logger setup returns the same instance each time.
    """
    logger1 = logger_module.logger
    logger2 = logger_module.setup_logger()
    assert logger1 is logger2


def test_logger_has_console_and_file_handlers():
    """
    Test that the logger has both console and file handlers attached.
    """
    logger = logger_module.logger
    handler_types = [type(h) for h in logger.handlers]

    assert logging.StreamHandler in handler_types, "Console handler missing"
    assert logging.FileHandler in handler_types, "File handler missing"
    assert logger.level == logging.INFO


def test_logger_logs_info_message(caplog):
    """
    Use caplog to check that info messages are emitted.
    """
    test_message = "This is a test log message"
    with caplog.at_level(logging.INFO, logger="tiktok_automation_logger"):
        logger_module.logger.info(test_message)

    assert any(test_message in record.message for record in caplog.records)
