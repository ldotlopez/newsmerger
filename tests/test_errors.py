import logging
import unittest

import requests

from newstool.errors import PluginFailure, describe, log_failure, reason


class DescribeTests(unittest.TestCase):
    def test_plugin_failure_is_its_message(self) -> None:
        self.assertEqual(describe(PluginFailure("empty summary")), "empty summary")

    def test_other_exceptions_keep_their_type(self) -> None:
        self.assertEqual(describe(ValueError("boom")), "ValueError: boom")
        self.assertEqual(
            describe(requests.ConnectionError("down")), "ConnectionError: down"
        )

    def test_type_alone_without_message(self) -> None:
        self.assertEqual(describe(TimeoutError()), "TimeoutError")

    def test_reason_is_the_message_or_the_type(self) -> None:
        self.assertEqual(reason(ValueError("boom")), "boom")
        self.assertEqual(reason(TimeoutError()), "TimeoutError")

    def test_plugin_failure_is_a_value_error(self) -> None:
        self.assertIsInstance(PluginFailure("x"), ValueError)


class LogFailureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger("newstool.test_errors")
        self.logger.setLevel(logging.WARNING)

    def record(self, exc: Exception, level: str = "ERROR") -> logging.LogRecord:
        with self.assertLogs(self.logger, level) as logs:
            log_failure(self.logger, "step failed", exc)
        return logs.records[0]

    def test_expected_failures_have_no_traceback(self) -> None:
        for exc in (PluginFailure("empty response"), requests.ConnectionError("x")):
            with self.subTest(exc=exc):
                self.assertIsNone(self.record(exc).exc_info)

    def test_message_names_the_failure(self) -> None:
        record = self.record(PluginFailure("empty response"))

        self.assertEqual(record.getMessage(), "step failed: empty response")

    def test_unexpected_failures_keep_the_traceback(self) -> None:
        for exc in (ValueError("x"), KeyError("x"), TypeError("x")):
            with self.subTest(exc=exc):
                self.assertIsNotNone(self.record(exc).exc_info)

    def test_traceback_with_debug_logging(self) -> None:
        record = self.record(PluginFailure("empty response"), level="DEBUG")

        self.assertIsNotNone(record.exc_info)
