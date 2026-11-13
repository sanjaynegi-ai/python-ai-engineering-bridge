"""Fixtures shared by every test. Do not edit.

Tests use the HashingEmbedder: deterministic, instant and free, with no model to
download. It matches words rather than meaning, which is enough to test the plumbing.
Modules you haven't written yet are imported inside fixtures, so that each milestone's
tests run as soon as that milestone is done.
"""

import os
import shutil
from pathlib import Path

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
    """No ASSISTANT_* variables, and an empty working folder, so no real .env is read."""
    for name in list(os.environ):
        if name.upper().startswith("ASSISTANT_"):
            monkeypatch.delenv(name)
    monkeypatch.chdir(tmp_path)
    return monkeypatch
