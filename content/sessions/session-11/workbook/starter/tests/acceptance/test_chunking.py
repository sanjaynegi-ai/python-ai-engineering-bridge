"""Acceptance tests for chunking (workbook Milestone 3). Do not edit."""

import pytest

from handbook_search.chunking import chunk_documents, split_sections, split_text
from handbook_search.loading import load_documents
from handbook_search.models import Chunk, Document

MARKDOWN = """# Runbook: Example

An introduction.

## Diagnose

Step one.

## Empty

## Fix

Step two.
"""


def test_split_sections_at_level_two_headings():
    assert split_sections(MARKDOWN) == [
        (None, "An introduction."),
        ("Diagnose", "Step one."),
        ("Fix", "Step two."),
    ]


def test_split_sections_without_headings():
    assert split_sections("Just text.\nMore text.") == [(None, "Just text.\nMore text.")]


def test_split_text_respects_the_size():
    text = " ".join(f"Sentence number {n} is here." for n in range(40))

    pieces = split_text(text, size=120, overlap=0)

    assert len(pieces) > 1
    assert all(len(piece) <= 120 for piece in pieces)


def test_split_text_keeps_sentences_whole():
    text = "First sentence is here. Second sentence is here. Third sentence is here."

    pieces = split_text(text, size=50, overlap=0)

    assert pieces == ["First sentence is here. Second sentence is here.", "Third sentence is here."]


def test_split_text_overlaps_neighbours():
    text = "Alpha one two. Beta three four. Gamma five six. Delta seven eight."

    pieces = split_text(text, size=35, overlap=20)

    assert pieces[0] == "Alpha one two. Beta three four."
    assert pieces[1].startswith("Beta three four.")  # the end of the previous piece, repeated


def test_split_text_normalises_whitespace():
    pieces = split_text("Line one continues\nacross lines.   Spaces   too.", size=500, overlap=0)

    assert pieces == ["Line one continues across lines. Spaces too."]


def test_a_unit_longer_than_the_size_is_its_own_piece():
    long_sentence = "word " * 60

    pieces = split_text(f"Short. {long_sentence.strip()}. End.", size=100, overlap=0)

    assert any(len(piece) > 100 for piece in pieces)
    assert pieces[0] == "Short."


def test_empty_text_gives_no_pieces():
    assert split_text("   \n  ", size=100, overlap=10) == []


@pytest.fixture
def chunks(handbook) -> list[Chunk]:
    documents, _ = load_documents(handbook)
    return chunk_documents(documents, size=500, overlap=100)


def test_handbook_chunks_have_sensible_sizes(chunks):
    assert 35 <= len(chunks) <= 70
    assert all(0 < len(chunk.text) <= 500 for chunk in chunks)


def test_markdown_chunks_keep_their_metadata(chunks):
    chunk = next(
        c for c in chunks if c.source == "runbook-vpn-outage.md" and c.section == "Diagnose"
    )

    assert chunk.title == "Runbook: Office VPN Problems"
    assert chunk.page is None
    assert "concentrator" in chunk.text


def test_title_lines_are_not_in_the_text(chunks):
    assert not any(chunk.text.startswith("# ") for chunk in chunks)


def test_pdf_chunks_keep_their_page_and_have_no_section(chunks):
    pdf = [c for c in chunks if c.source == "policy-incident-communication.pdf"]

    assert {c.page for c in pdf} == {1, 2}
    assert {c.section for c in pdf} == {None}


def test_indexes_count_per_file_from_zero(chunks):
    for source in {c.source for c in chunks}:
        indexes = [c.index for c in chunks if c.source == source]
        assert indexes == list(range(len(indexes))), source


def test_chunking_is_deterministic(handbook):
    documents, _ = load_documents(handbook)

    assert chunk_documents(documents, size=500, overlap=100) == chunk_documents(
        documents, size=500, overlap=100
    )


def test_smaller_size_gives_more_chunks(handbook):
    documents, _ = load_documents(handbook)

    assert len(chunk_documents(documents, size=150, overlap=30)) > len(
        chunk_documents(documents, size=500, overlap=100)
    )


def test_a_pdf_page_chunk_index_continues_across_pages():
    pages = [
        Document("p.pdf", "P", "Page one text.", page=1),
        Document("p.pdf", "P", "Page two text.", page=2),
    ]

    chunks = chunk_documents(pages, size=500, overlap=0)

    assert [(c.page, c.index) for c in chunks] == [(1, 0), (2, 1)]


def test_pdf_pages_are_never_split_into_sections():
    page = Document("p.pdf", "P", "## Not a heading in a PDF\nBody text.", page=1)

    chunks = chunk_documents([page], size=500, overlap=0)

    assert [(c.section, c.text) for c in chunks] == [(None, "## Not a heading in a PDF Body text.")]
