"""Structured logging: one JSON object per line, with a request ID on every record.

The request ID part is provided: REQUEST_ID holds the current request's ID (the API
sets it), and install_request_ids() makes every log record carry it as
`record.request_id`, so all the lines one request produces can be found together.
"""

import contextvars
import json  # noqa: F401  (you'll need these in JsonFormatter)
import logging
import sys  # noqa: F401
from datetime import UTC, datetime  # noqa: F401
from typing import TextIO

REQUEST_ID: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)

# Attributes every LogRecord has. Anything else on a record came from `extra=`.
STANDARD_ATTRIBUTES = set(vars(logging.LogRecord("", 0, "", 0, "", None, None))) | {
    "message",
    "asctime",
    "request_id",
}

_installed = False


def install_request_ids() -> None:
    """Make every new LogRecord carry the current REQUEST_ID as `request_id`. Idempotent."""
    global _installed
    if _installed:
        return
    original = logging.getLogRecordFactory()

    def factory(*args, **kwargs) -> logging.LogRecord:
        record = original(*args, **kwargs)
        record.request_id = REQUEST_ID.get()
        return record

    logging.setLogRecordFactory(factory)
    _installed = True


class JsonFormatter(logging.Formatter):
    """Formats a record as one line of JSON.

    Always: "time" (UTC, ISO 8601, milliseconds), "level", "logger", "message".
    Then "request_id" if the record has one that isn't None, every field passed with
    `extra=`, and "exception" (the exception's type name only) if the record has
    exception information. Values JSON can't represent are written with str().
    """

    def format(self, record: logging.LogRecord) -> str:
        # TODO Milestone 2
        raise NotImplementedError


def configure_logging(
    level: int = logging.INFO, *, json_format: bool = False, stream: TextIO | None = None
) -> None:
    """Send the application's logs to `stream` (default: stderr), as JSON or as text.

    Text lines look like "INFO knowledge_assistant.api: request". Replaces any handler
    this function added before, so calling it twice doesn't duplicate every line. Also
    calls install_request_ids(), and sets the "pypdf" logger to ERROR (it logs the
    first bytes of broken files) and "httpx2" to WARNING (it logs every request).
    """
    # TODO Milestone 2
    raise NotImplementedError
