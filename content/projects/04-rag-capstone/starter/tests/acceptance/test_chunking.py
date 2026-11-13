"""Milestone 3: chunking one file's documents. Do not edit."""

import re

import pytest

from knowledge_assistant.chunking import chunk_document
from knowledge_assistant.documents import load_document
from knowledge_assistant.models import Document

HASH = "f" * 64

RUNBOOK = """# Runbook: Example

Intro text before any section.

## Diagnose

Check the dashboard. Then check the logs.

## Fix

Restart the service.
"""


def words(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9]+", text))


def sentences(count: int) -> str:
    return " ".join(f"Sentence number {n} is here." for n in range(count))


def test_markdown_chunks_record_their_section():
    document = Document(source="runbooks/example.md", title="Runbook: Example", text=RUNBOOK)
    chunks = chunk_document([document], HASH, size=800, overlap=100)
    assert [(chunk.section, chunk.text) for chunk in chunks] == [
        (None, "Intro text before any section."),
        ("Diagnose", "Check the dashboard. Then check the logs."),
        ("Fix", "Restart the service."),
    ]


def test_chunks_carry_source_title_hash_and_consecutive_indexes():
    document = Document(source="runbooks/example.md", title="Runbook: Example", text=RUNBOOK)
    chunks = chunk_document([document], HASH, size=800, overlap=100)
    assert [chunk.index for chunk in chunks] == [0, 1, 2]
    assert {chunk.source for chunk in chunks} == {"runbooks/example.md"}
    assert {chunk.title for chunk in chunks} == {"Runbook: Example"}
    assert {chunk.content_hash for chunk in chunks} == {HASH}
    assert {chunk.page for chunk in chunks} == {None}


def test_headings_are_metadata_not_chunk_text():
    document = Document(source="a.md", title="Runbook: Example", text=RUNBOOK)
    chunks = chunk_document([document], HASH, size=800, overlap=100)
    assert not any(chunk.text.lstrip().startswith("#") for chunk in chunks)
    assert not any("Runbook: Example" in chunk.text for chunk in chunks)


@pytest.mark.parametrize("size", [120, 300, 800])
def test_every_chunk_fits_and_no_text_is_lost(docs, size):
    for path in sorted((docs / "runbooks").glob("*.md")):
        source = f"runbooks/{path.name}"
        [document] = load_document(path, source)
        chunks = chunk_document([document], HASH, size=size, overlap=size // 5)
        assert all(0 < len(chunk.text) <= size for chunk in chunks), source
        assert all(chunk.text.strip() for chunk in chunks), source
        body = "\n".join(
            line for line in document.text.splitlines() if not line.startswith(("# ", "## "))
        )
        covered = set().union(*(words(chunk.text) for chunk in chunks))
        assert words(body) <= covered, source


def test_long_sections_are_split_with_overlap():
    text = "## Long\n\n" + sentences(40)
    document = Document(source="a.md", title="A", text=text)
    chunks = chunk_document([document], HASH, size=200, overlap=60)
    assert len(chunks) > 1
    assert {chunk.section for chunk in chunks} == {"Long"}
    shared = [
        set(re.findall(r"Sentence number \d+ ", first.text))
        & set(re.findall(r"Sentence number \d+ ", second.text))
        for first, second in zip(chunks, chunks[1:], strict=False)
    ]
    assert all(shared), "consecutive chunks should repeat some text"


def test_zero_overlap_repeats_nothing():
    document = Document(source="a.md", title="A", text="## Long\n\n" + sentences(40))
    chunks = chunk_document([document], HASH, size=200, overlap=0)
    found = [n for chunk in chunks for n in re.findall(r"Sentence number (\d+) is", chunk.text)]
    assert len(found) == len(set(found))


def test_pdf_pages_are_chunked_separately_with_page_numbers(docs):
    documents = load_document(docs / "policies" / "on-call-rota.pdf", "policies/on-call-rota.pdf")
    chunks = chunk_document(documents, HASH, size=300, overlap=50)
    assert {chunk.page for chunk in chunks} == {1, 2}
    assert {chunk.section for chunk in chunks} == {None}
    assert [chunk.index for chunk in chunks] == list(range(len(chunks)))
    pages = [chunk.page for chunk in chunks]
    assert pages == sorted(pages)
    page_one = {chunk.text for chunk in chunks if chunk.page == 1}
    assert not any("Swaps" in text for text in page_one)


def test_pdf_text_is_never_read_as_markdown_headings():
    text = "# 1. Scope\n## Not a heading either\nThe body of the page."
    document = Document(source="p.pdf", title="P", text=text, page=1)
    chunks = chunk_document([document], HASH, size=800, overlap=100)
    assert {chunk.section for chunk in chunks} == {None}
    assert words(text) <= set().union(*(words(chunk.text) for chunk in chunks))


def test_no_documents_give_no_chunks():
    assert chunk_document([], HASH, size=800, overlap=100) == []


def test_a_title_only_file_gives_no_chunks():
    document = Document(source="a.md", title="Only a title", text="# Only a title\n")
    assert chunk_document([document], HASH, size=800, overlap=100) == []
