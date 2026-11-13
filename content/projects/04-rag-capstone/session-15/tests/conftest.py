"""Fixtures shared by every test. Do not edit.

Tests use the HashingEmbedder: deterministic, instant and free, with no model to
download. It matches words rather than meaning, which is enough to test the plumbing.
No test makes a real API call: generators are scripted, and `fake_openai` stands in for
OpenAI's Responses API at the HTTP level.
Modules you haven't written yet are imported inside fixtures, so that each milestone's
tests run as soon as that milestone is done.
"""

import json
import os
import shutil
from pathlib import Path

import httpx2
import pytest
from pypdf import PdfWriter

DOCS = Path(__file__).parents[1] / "data" / "docs"


@pytest.fixture
def docs(tmp_path) -> Path:
    """A private copy of the sample documents, safe to change."""
    target = tmp_path / "docs"
    shutil.copytree(DOCS, target)
    return target


@pytest.fixture
def embedder():
    from knowledge_assistant.embedding import HashingEmbedder

    return HashingEmbedder()


class CountingEmbedder:
    """Wraps an embedder, and records every text it's asked to embed.

    With `fail_on`, it raises RuntimeError for any batch containing that text, like a
    provider that goes down in the middle of a run.
    """

    def __init__(self, inner, fail_on: str | None = None) -> None:
        self.inner = inner
        self.model_id = inner.model_id
        self.dimensions = inner.dimensions
        self.calls = 0
        self.texts: list[str] = []
        self.fail_on = fail_on

    def embed(self, texts):
        self.calls += 1
        if self.fail_on and any(self.fail_on in text for text in texts):
            raise RuntimeError("embedding service unavailable")
        self.texts.extend(texts)
        return self.inner.embed(texts)


@pytest.fixture
def counting_embedder(embedder) -> CountingEmbedder:
    return CountingEmbedder(embedder)


@pytest.fixture
def config(embedder):
    """The index configuration that matches the `embedder` fixture."""
    from knowledge_assistant.models import IndexConfig

    return IndexConfig(
        embedding_model=embedder.model_id,
        dimensions=embedder.dimensions,
        chunk_size=800,
        chunk_overlap=100,
    )


@pytest.fixture
def index_dir(tmp_path) -> Path:
    return tmp_path / "index"


@pytest.fixture
def store(index_dir, config):
    """An empty index in a temporary folder."""
    from knowledge_assistant.store import ChunkStore

    return ChunkStore(index_dir, config)


@pytest.fixture
def make_chunk():
    """A factory for chunks, with any fields overridden."""
    from knowledge_assistant.models import Chunk

    def _make_chunk(text: str = "Check the load balancer first.", **overrides) -> "Chunk":
        fields = {
            "text": text,
            "source": "runbooks/example.md",
            "title": "Runbook: Example",
            "section": "Diagnose",
            "page": None,
            "index": 0,
            "content_hash": "a" * 64,
        }
        return Chunk(**(fields | overrides))

    return _make_chunk


@pytest.fixture
def blank_pdf(tmp_path) -> Path:
    """A valid PDF whose only page has no text, like a scanned document."""
    path = tmp_path / "scanned.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    with open(path, "wb") as file:
        writer.write(file)
    return path


@pytest.fixture
def clean_env(monkeypatch, tmp_path):
    """No ASSISTANT_*, LLM or provider variables, and an empty working folder (no .env)."""
    for name in list(os.environ):
        if name.upper().startswith(("ASSISTANT_", "LLM_", "OPENAI_")):
            monkeypatch.delenv(name)
    monkeypatch.chdir(tmp_path)
    return monkeypatch


# -- Session 15 ------------------------------------------------------------------------------


def response_body(
    output_text: str | None = None,
    *,
    refusal: str | None = None,
    status: str = "completed",
    model: str = "gpt-5.6-terra",
    input_tokens: int = 900,
    output_tokens: int = 80,
) -> dict:
    """A Responses API reply with one assistant message: text, or a refusal."""
    if refusal is not None:
        content = [{"type": "refusal", "refusal": refusal}]
    else:
        content = [{"type": "output_text", "text": output_text or "", "annotations": []}]
    return {
        "id": "resp_test_0001",
        "object": "response",
        "created_at": 1761120000,
        "model": model,
        "status": status,
        "incomplete_details": None,
        "error": None,
        "instructions": None,
        "metadata": {},
        "parallel_tool_calls": True,
        "temperature": None,
        "tool_choice": "auto",
        "tools": [],
        "top_p": None,
        "output": [
            {
                "type": "message",
                "id": "msg_test_0001",
                "role": "assistant",
                "status": status,
                "content": content,
            }
        ],
        "usage": {
            "input_tokens": input_tokens,
            "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
            "output_tokens": output_tokens,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": input_tokens + output_tokens,
        },
    }


def answer_body(answer: str = "Run the promotion job [1].", citations=(1,), answerable=True):
    """A successful reply whose text is a GroundedAnswer."""
    payload = {"answerable": answerable, "answer": answer, "citations": list(citations)}
    return response_body(json.dumps(payload))


class FakeOpenAI:
    """OpenAI's Responses API, faked at the HTTP level, as in Project 03.

    Replays scripted replies in order (the last one repeats) and records every request.
    Entries are a dict (a 200 reply), a (status, body) tuple, or an exception to raise.
    """

    reply = staticmethod(response_body)
    answer_reply = staticmethod(answer_body)

    def __init__(self) -> None:
        self.script: list = [answer_body()]
        self.requests: list[httpx2.Request] = []

    @property
    def bodies(self) -> list[dict]:
        return [json.loads(request.content) for request in self.requests]

    def handler(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(request)
        entry = self.script.pop(0) if len(self.script) > 1 else self.script[0]
        if isinstance(entry, Exception):
            raise entry
        if isinstance(entry, tuple):
            status, body = entry
            return httpx2.Response(status, json=body, headers={"retry-after-ms": "1"})
        return httpx2.Response(200, json=entry)

    def http_client(self) -> httpx2.Client:
        return httpx2.Client(transport=httpx2.MockTransport(self.handler))


@pytest.fixture
def fake_openai() -> FakeOpenAI:
    return FakeOpenAI()


class ScriptedGenerator:
    """A Generator that returns a scripted answer, or raises, and records every call."""

    model_id = "scripted"

    def __init__(self) -> None:
        self.answerable = True
        self.answer = "Run the promotion job [1]."
        self.citations: list[int] = [1]
        self.error: Exception | None = None
        self.calls: list[tuple[str, str]] = []  # (question, context)

    def generate(self, question: str, context: str):
        from knowledge_assistant.generation import Generation, GroundedAnswer

        self.calls.append((question, context))
        if self.error is not None:
            raise self.error
        result = GroundedAnswer(
            answerable=self.answerable, answer=self.answer, citations=self.citations
        )
        return Generation(result, model="scripted-model", input_tokens=500, output_tokens=40)


@pytest.fixture
def generator() -> ScriptedGenerator:
    return ScriptedGenerator()


@pytest.fixture
def ingested(docs, store, embedder):
    """The `store` fixture, with the sample documents ingested."""
    from knowledge_assistant.ingestion import ingest

    ingest(docs, store, embedder)
    return store


@pytest.fixture
def assistant(ingested, embedder, generator):
    """An Assistant over the ingested sample documents, with the scripted generator."""
    from knowledge_assistant.assistant import Assistant

    return Assistant(store=ingested, embedder=embedder, generator=generator, top_k=4, min_score=0.2)


@pytest.fixture
def make_hit(make_chunk):
    """A factory for search hits: make_hit(score, text, **chunk_fields)."""
    from knowledge_assistant.models import Hit

    def _make_hit(score: float = 0.8, text: str = "Check the load balancer.", **fields) -> "Hit":
        return Hit(score=score, chunk=make_chunk(text, **fields))

    return _make_hit
