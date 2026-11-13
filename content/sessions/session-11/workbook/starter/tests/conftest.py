"""Fixtures shared by every test. Do not edit.

Tests use the HashingEmbedder: deterministic, instant, and free, with no model to
download. It matches words rather than meaning, which is enough to test the plumbing.
"""

import os
import shutil
from pathlib import Path

import pytest
from pypdf import PdfWriter

HANDBOOK = Path(__file__).parents[1] / "data" / "handbook"


@pytest.fixture
def handbook(tmp_path) -> Path:
    """A private copy of the sample handbook."""
    target = tmp_path / "handbook"
    shutil.copytree(HANDBOOK, target)
    return target


@pytest.fixture
def embedder():
    from handbook_search.embedding import HashingEmbedder

    return HashingEmbedder()


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
def make_chunk():
    """A factory for chunks, with any fields overridden."""
    from handbook_search.models import Chunk

    def _make_chunk(text: str = "Check the load balancer first.", **overrides) -> Chunk:
        fields = {
            "text": text,
            "source": "runbook.md",
            "title": "Runbook",
            "section": "Diagnose",
            "page": None,
            "index": 0,
        }
        return Chunk(**(fields | overrides))

    return _make_chunk


@pytest.fixture
def clean_env(monkeypatch, tmp_path):
    """No HANDBOOK_* variables, and an empty working folder, so no real .env is read."""
    for name in list(os.environ):
        if name.upper().startswith("HANDBOOK_"):
            monkeypatch.delenv(name)
    monkeypatch.chdir(tmp_path)
    return monkeypatch
