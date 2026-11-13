"""Session 15, Milestone 3: the HTTP API. Do not edit."""

import pytest
from fastapi.testclient import TestClient

from knowledge_assistant.answering import NOT_FOUND
from knowledge_assistant.api import create_app
from knowledge_assistant.errors import (
    GeneratorConfigurationError,
    GeneratorUnavailable,
    InvalidAnswerError,
)

QUESTION = "How do I promote the orders database replica?"


@pytest.fixture
def client(assistant):
    return TestClient(create_app(assistant))


def test_health_reports_the_index(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "files": 24, "chunks": response.json()["chunks"]}
    assert response.json()["chunks"] > 24


def test_ask_returns_an_answer_with_sources(client, generator):
    generator.answer = "Run the promotion job [1]."
    response = client.post("/ask", json={"question": QUESTION})
    assert response.status_code == 200
    body = response.json()
    assert body["found"] is True
    assert body["answer"] == "Run the promotion job [1]."
    assert body["question"] == QUESTION
    [source] = body["sources"]
    assert source["number"] == 1
    assert source["source"] == "runbooks/database-failover.md"
    assert set(source) >= {"title", "section", "page", "score", "citation"}


def test_a_question_the_documents_do_not_answer_is_200_not_found(client, generator):
    generator.answerable = False
    generator.answer = ""
    generator.citations = []
    response = client.post("/ask", json={"question": "What's on the cafeteria menu?"})
    assert response.status_code == 200
    assert response.json()["found"] is False
    assert response.json()["answer"] == NOT_FOUND
    assert response.json()["sources"] == []


@pytest.mark.parametrize(
    "payload",
    [{}, {"question": ""}, {"question": "    "}, {"question": "x" * 1001}, {"question": 42}],
    ids=["missing", "empty", "blank", "too-long", "not-a-string"],
)
def test_invalid_questions_are_422(client, generator, payload):
    response = client.post("/ask", json=payload)
    assert response.status_code == 422
    assert generator.calls == []


@pytest.mark.parametrize(
    ("error", "status"),
    [
        (GeneratorUnavailable("timed out after retries"), 503),
        (InvalidAnswerError("cites [7]"), 502),
        (GeneratorConfigurationError("the provider rejected the API key (401)"), 500),
    ],
)
def test_generator_failures_map_to_status_codes(client, generator, error, status):
    generator.error = error
    response = client.post("/ask", json={"question": QUESTION})
    assert response.status_code == status
    detail = response.json()["detail"]
    assert isinstance(detail, str) and detail
    assert "Traceback" not in response.text


def test_an_ungrounded_answer_is_502(client, generator):
    generator.answer = "Promote it [9]."
    generator.citations = [9]
    assert client.post("/ask", json={"question": QUESTION}).status_code == 502


def test_the_openapi_schema_documents_ask(client):
    schema = client.get("/openapi.json").json()
    ask = schema["paths"]["/ask"]["post"]
    assert "requestBody" in ask
    response_schema = ask["responses"]["200"]["content"]["application/json"]["schema"]
    assert response_schema == {"$ref": "#/components/schemas/Answer"}
