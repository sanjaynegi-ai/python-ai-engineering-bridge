"""Session 16, Milestone 1: the logging setup. Do not edit."""

import io
import json
import logging

import pytest

from knowledge_assistant.logging_setup import REQUEST_ID, JsonFormatter, configure_logging

QUESTION = "How do I promote the orders database replica?"


def make_record(message="answer", level=logging.INFO, exc_info=None, **extra):
    record = logging.getLogger("knowledge_assistant.test").makeRecord(
        "knowledge_assistant.test", level, __file__, 1, message, (), exc_info, extra=extra
    )
    return record


def events(caplog, name):
    return [r for r in caplog.records if getattr(r, "event", None) == name]


@pytest.fixture(autouse=True)
def restore_logging():
    """Leave the root logger as the test found it."""
    root = logging.getLogger()
    handlers, level = list(root.handlers), root.level
    yield
    for handler in list(root.handlers):
        if handler not in handlers:
            root.removeHandler(handler)
    root.setLevel(level)


# -- JsonFormatter ------------------------------------------------------------------------------


def test_a_record_is_one_line_of_json_with_the_standard_fields():
    line = JsonFormatter().format(make_record("index ready", level=logging.WARNING))
    assert "\n" not in line
    entry = json.loads(line)
    assert entry["level"] == "WARNING"
    assert entry["logger"] == "knowledge_assistant.test"
    assert entry["message"] == "index ready"
    assert entry["time"].endswith("+00:00")  # UTC
    assert "T" in entry["time"]


def test_extra_fields_become_json_fields():
    entry = json.loads(JsonFormatter().format(make_record(event="answer", found=True, hits=4)))
    assert entry["event"] == "answer"
    assert entry["found"] is True
    assert entry["hits"] == 4


def test_standard_record_attributes_are_not_dumped():
    entry = json.loads(JsonFormatter().format(make_record(event="x")))
    for noise in ("args", "msg", "pathname", "lineno", "thread", "processName", "levelno"):
        assert noise not in entry


def test_values_json_cannot_represent_are_written_as_text():
    from pathlib import PurePosixPath

    entry = json.loads(JsonFormatter().format(make_record(where=PurePosixPath("index/x"))))
    assert entry["where"] == "index/x"


def test_an_exception_is_logged_by_type_only():
    try:
        raise ValueError("CANARY-77 the text that caused it")
    except ValueError:
        import sys

        record = make_record("failed", level=logging.ERROR, exc_info=sys.exc_info())
    line = JsonFormatter().format(record)
    assert json.loads(line)["exception"] == "ValueError"
    assert "CANARY" not in line


def test_the_request_id_is_included_when_there_is_one():
    configure_logging(stream=io.StringIO())  # installs request IDs on new records
    token = REQUEST_ID.set("req-123")
    try:
        record = make_record("inside a request")
    finally:
        REQUEST_ID.reset(token)
    assert json.loads(JsonFormatter().format(record))["request_id"] == "req-123"
    outside = json.loads(JsonFormatter().format(make_record("outside")))
    assert "request_id" not in outside


# -- configure_logging ---------------------------------------------------------------------------


def test_configure_logging_writes_json_lines_to_the_stream():
    stream = io.StringIO()
    configure_logging(logging.INFO, json_format=True, stream=stream)
    logging.getLogger("knowledge_assistant.demo").info("hello", extra={"event": "demo"})
    [line] = stream.getvalue().splitlines()
    assert json.loads(line)["event"] == "demo"


def test_configuring_twice_does_not_duplicate_lines():
    first, second = io.StringIO(), io.StringIO()
    configure_logging(json_format=True, stream=first)
    configure_logging(json_format=True, stream=second)
    logging.getLogger("knowledge_assistant.demo").warning("once")
    assert first.getvalue() == ""
    assert len(second.getvalue().splitlines()) == 1


def test_text_format_is_still_available():
    stream = io.StringIO()
    configure_logging(logging.INFO, json_format=False, stream=stream)
    logging.getLogger("knowledge_assistant.demo").info("plain")
    assert stream.getvalue().strip() == "INFO knowledge_assistant.demo: plain"
