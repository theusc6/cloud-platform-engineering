"""Tests for the structured logger."""

import logging

from cpe_project.core.logger import get_logger


class TestGetLogger:
    def test_returns_logger_with_cpe_prefix(self):
        log = get_logger("TestModule")
        assert log.name == "cpe.TestModule"

    def test_default_level_is_info(self):
        log = get_logger("TestLevel")
        assert log.level == logging.INFO

    def test_custom_level(self):
        log = get_logger("DebugModule", level=logging.DEBUG)
        assert log.level == logging.DEBUG

    def test_has_handler(self):
        log = get_logger("HandlerTest")
        assert len(log.handlers) >= 1

    def test_same_logger_returned_on_repeat_call(self):
        log1 = get_logger("Repeat")
        log2 = get_logger("Repeat")
        assert log1 is log2
