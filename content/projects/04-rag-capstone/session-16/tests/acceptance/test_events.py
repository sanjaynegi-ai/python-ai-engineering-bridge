"""Session 16, Milestone 3: the events that answering, ingestion and the API log. Do not edit."""

import io
import logging

import pytest
from fastapi.testclient import TestClient

from knowledge_assistant.answering import answer_question
from knowledge_assistant.ingestion import ingest
from knowledge_assistant.logging_setup import configure_logging

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


# -- events ---------------------------------------------------------------------------------------


def test_each_answer_logs_one_answer_event(assistant, generator, caplog):
    caplog.set_level(logging.INFO)
    answer_question(
        f"{QUESTION} CANARY-Q-51",
        store=assistant.store,
        embedder=assistant.embedder,
        generator=generator,
        top_k=4,
        min_score=0.2,
    )
    [record] = events(caplog, "answer")
    assert record.levelno == logging.INFO
    assert record.found is True
    assert record.hits == 4
    assert record.sources == 1
    assert record.model == "scripted-model"
    assert (record.input_tokens, record.output_tokens) == (500, 40)
    assert record.duration_ms >= 0
    assert "CANARY" not in caplog.text


def test_a_not_found_answer_is_logged_too(assistant, generator, caplog):
    caplog.set_level(logging.INFO)
    assistant.min_score = 1.01
    assistant.ask(QUESTION)
    [record] = events(caplog, "answer")
    assert record.found is False
    assert record.hits == 0
    assert record.sources == 0
    assert record.model is None


def test_ingestion_logs_one_summary_event(docs, store, embedder, caplog):
    caplog.set_level(logging.INFO)
    (docs / "guides" / "empty.md").write_bytes(b"")
    ingest(docs, store, embedder)
    [record] = events(caplog, "ingest")
    assert (record.added, record.updated, record.unchanged) == (24, 0, 0)
    assert (record.removed, record.failed) == (0, 1)
    assert record.chunks_written == store.count()
    assert record.duration_ms >= 0


def test_every_api_request_is_logged_with_an_id(assistant, caplog):
    from knowledge_assistant.api import create_app

    configure_logging(stream=io.StringIO())
    caplog.set_level(logging.INFO)
    client = TestClient(create_app(assistant))

    response = client.post("/ask", json={"question": QUESTION})

    request_id = response.headers["X-Request-ID"]
    assert request_id
    [request] = events(caplog, "request")
    assert (request.method, request.path, request.status) == ("POST", "/ask", 200)
    assert request.duration_ms >= 0
    assert request.request_id == request_id
    [answer] = events(caplog, "answer")
    assert answer.request_id == request_id  # one ID ties the request to its answer


def test_a_safe_incoming_request_id_is_reused_and_an_unsafe_one_replaced(assistant):
    from knowledge_assistant.api import create_app

    client = TestClient(create_app(assistant))
    reused = client.get("/health", headers={"X-Request-ID": "trace-42-abc"})
    assert reused.headers["X-Request-ID"] == "trace-42-abc"
    replaced = client.get("/health", headers={"X-Request-ID": "bad id\nwith newline"})
    assert replaced.headers["X-Request-ID"] != "bad id\nwith newline"
    assert replaced.headers["X-Request-ID"]
    assert client.get("/health").headers["X-Request-ID"] != replaced.headers["X-Request-ID"]


def test_failed_requests_are_logged_with_their_status(assistant, generator, caplog):
    from knowledge_assistant.api import create_app
    from knowledge_assistant.errors import GeneratorUnavailable

    caplog.set_level(logging.INFO)
    generator.error = GeneratorUnavailable("timed out")
    response = TestClient(create_app(assistant)).post("/ask", json={"question": QUESTION})
    assert response.status_code == 503
    [request] = events(caplog, "request")
    assert request.status == 503
