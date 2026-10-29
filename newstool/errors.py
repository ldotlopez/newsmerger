from __future__ import annotations

import logging

import ollama
import requests
import sqlalchemy.exc


class PluginFailure(ValueError):
    """A plugin could not do its job in an expected way: an invalid LLM
    response, a page without the expected structure, an API that rejects a
    delivery... Its message is written for the user. It is a `ValueError` so
    the `except ValueError` of plugins that skip bad entries keep working."""


# Failures of what lies outside the program, reported as a message too.
EXTERNAL_ERRORS = (
    requests.RequestException,
    ollama.ResponseError,
    ConnectionError,
    TimeoutError,
    sqlalchemy.exc.OperationalError,
)

# Failures the user is told about with a message; the traceback only with
# debug logging. Any other exception is unexpected: its traceback is always
# shown.
EXPECTED_ERRORS = (PluginFailure, *EXTERNAL_ERRORS)


def describe(exc: BaseException) -> str:
    """What to tell the user: the message of a `PluginFailure`, `Type: message`
    for any other exception, or just the type when it has no message."""
    message = str(exc)
    if isinstance(exc, PluginFailure) and message:
        return message
    return f"{type(exc).__name__}: {message}" if message else type(exc).__name__


def reason(exc: BaseException) -> str:
    """The text stored as the error of a failed run: the message, or the type
    when it has none."""
    return str(exc) or type(exc).__name__


def log_failure(logger: logging.Logger, message: str, exc: Exception) -> None:
    """Log `message` and what `exc` says at error level; the traceback only
    with debug logging, or when `exc` is unexpected."""
    show_traceback = logger.isEnabledFor(logging.DEBUG) or not isinstance(
        exc, EXPECTED_ERRORS
    )
    logger.error(
        f"{message}: {describe(exc)}", exc_info=exc if show_traceback else None
    )
