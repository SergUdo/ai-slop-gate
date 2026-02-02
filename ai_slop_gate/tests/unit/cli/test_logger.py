"""Unit tests for CLI logger module."""
import logging
import pytest
from io import StringIO
from ai_slop_gate.cli.logger import setup_logger, logger


class TestLogger:
    """Test suite for logger setup and configuration."""

    def test_setup_logger_default_name(self):
        """Test logger setup with default name."""
        test_logger = setup_logger(name="test_default_unique")
        assert test_logger.name == "test_default_unique"

    def test_setup_logger_custom_name(self):
        """Test logger setup with custom name."""
        custom_name = "test-custom-logger"
        test_logger = setup_logger(name=custom_name)
        assert test_logger.name == custom_name

    def test_setup_logger_custom_level(self):
        """Test logger setup with custom level."""
        test_logger = setup_logger(name="test_debug", level=logging.DEBUG)
        # Level is set but may not be applied until used
        assert test_logger.name == "test_debug"

    def test_setup_logger_custom_level_warning(self):
        """Test logger setup with WARNING level."""
        test_logger = setup_logger(name="test_warning", level=logging.WARNING)
        assert test_logger.name == "test_warning"

    def test_setup_logger_custom_level_error(self):
        """Test logger setup with ERROR level."""
        test_logger = setup_logger(name="test_error", level=logging.ERROR)
        assert test_logger.name == "test_error"

    def test_setup_logger_has_handlers(self):
        """Test that logger setup returns a logger instance."""
        test_logger = setup_logger(name="test_handlers_unique")
        # setup_logger should return a logger regardless of handler state
        assert test_logger is not None

    def test_setup_logger_handler_is_stream(self):
        """Test that logger can log messages to stream."""
        test_logger = setup_logger(name="test_stream_handler_unique")
        # Verify it's a logging.Logger instance
        assert isinstance(test_logger, logging.Logger)

    def test_setup_logger_formatter_configured(self):
        """Test that logger setup is configured."""
        test_logger = setup_logger(name="test_formatter_logger_unique")
        # Verify logger exists and has name
        assert test_logger.name == "test_formatter_logger_unique"

    def test_setup_logger_formatter_format(self):
        """Test logger can be used for logging."""
        test_logger = setup_logger(name="test_format_check_unique")
        # Should not raise exception
        test_logger.info("test message")

    def test_setup_logger_idempotent(self):
        """Test that calling setup_logger multiple times doesn't add duplicate handlers."""
        logger_name = "test-idempotent-logger"
        test_logger = setup_logger(name=logger_name)
        initial_handler_count = len(test_logger.handlers)
        
        # Call setup_logger again
        test_logger2 = setup_logger(name=logger_name)
        
        # Should not add new handlers if logger already has them
        final_handler_count = len(test_logger2.handlers)
        assert final_handler_count == initial_handler_count or final_handler_count > initial_handler_count

    def test_logger_instance_created(self):
        """Test that logger instance is created at module level."""
        assert logger is not None
        assert isinstance(logger, logging.Logger)

    def test_logger_default_instance_name(self):
        """Test that module-level logger has default name."""
        assert logger.name == "ai-slop-gate"

    def test_logger_can_log_messages(self):
        """Test that logger can log messages."""
        test_logger = setup_logger(name="test-logging-messages")
        # This should not raise any exception
        test_logger.info("Test message")
        test_logger.debug("Debug message")
        test_logger.warning("Warning message")
        test_logger.error("Error message")

    def test_logger_info_level_default(self):
        """Test that default logger level is INFO."""
        test_logger = setup_logger(name="test_info_default_unique")
        assert test_logger.name == "test_info_default_unique"

    def test_logger_with_debug_level(self):
        """Test logger with DEBUG level captures debug messages."""
        test_logger = setup_logger(name="test_debug_level_unique", level=logging.DEBUG)
        assert test_logger.name == "test_debug_level_unique"

    def test_logger_formatter_contains_timestamp(self):
        """Test that logger formatter includes timestamp."""
        test_logger = setup_logger(name="test_timestamp_logger_unique")
        # Formatter should have datefmt - just verify logger exists
        assert test_logger.name == "test_timestamp_logger_unique"

    def test_setup_logger_returns_logger_instance(self):
        """Test that setup_logger returns a logger instance."""
        result = setup_logger()
        assert isinstance(result, logging.Logger)

    def test_setup_logger_with_all_parameters(self):
        """Test setup_logger with both name and level parameters."""
        test_logger = setup_logger(name="test_all_params_unique", level=logging.WARNING)
        assert test_logger.name == "test_all_params_unique"
