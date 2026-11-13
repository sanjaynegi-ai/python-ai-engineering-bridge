"""Acceptance tests for retrieval, context and citations (workbook Milestone 5). Do not edit."""

import pytest

from handbook_search.chunking import chunk_documents
from handbook_search.loading import load_documents
from handbook_search.models import Hit
from handbook_search.retrieval import build_context, cited_numbers, retrieve
from handbook_search.store import VectorStore


@pytest.fixture
def store(handbook, embedder) -> VectorStore:
    documents, _ = load_documents(handbook)
    chunks = chunk_documents(documents, size=500, overlap=100)
    store = VectorStore(embedder.model_id, embedder.dimensions)
    store.add(chunks, embedder.embed([c.embedding_text for c in chunks]))
    return store


def test_retrieve_finds_the_matching_runbook(store, embedder):
    hits = retrieve(store, embedder, "promote the replica db-03 database", k=3, min_score=0.0)

    assert hits[0].chunk.source == "runbook-database-failover.md"
    assert len(hits) == 3


def test_section_headings_are_searchable(store, embedder):
    # "Check first" is a section heading, not text in the chunk. It's found because the
    # chunk's embedding_text includes its section (the fixture embeds it, as ingest does).
    hits = retrieve(store, embedder, "check first", k=1, min_score=0.0)

    assert hits[0].chunk.section == "Check first"


def test_retrieve_returns_nothing_below_the_minimum(store, embedder):
    assert retrieve(store, embedder, "cafeteria menu", k=3, min_score=0.3) == []


def test_retrieve_rejects_an_empty_question(store, embedder):
    with pytest.raises(ValueError):
        retrieve(store, embedder, "   ", k=3, min_score=0.0)


def test_build_context_numbers_the_sources(make_chunk):
    hits = [
        Hit(0.9, make_chunk("Check the load balancer.", source="runbook.md", section="Diagnose")),
        Hit(0.8, make_chunk("Targets are hours.", source="sla.pdf", section=None, page=2)),
    ]

    assert build_context(hits) == (
        "[1] (runbook.md, Diagnose)\nCheck the load balancer.\n\n"
        "[2] (sla.pdf, page 2)\nTargets are hours."
    )


def test_build_context_of_nothing_is_empty():
    assert build_context([]) == ""


def test_cited_numbers(make_chunk):
    hits = [Hit(0.9, make_chunk()), Hit(0.8, make_chunk()), Hit(0.7, make_chunk())]

    assert cited_numbers("Do this [2], then that [1] and [2].", hits) == [1, 2]
    assert cited_numbers("No citations at all.", hits) == []


def test_cited_numbers_rejects_sources_that_were_not_sent(make_chunk):
    hits = [Hit(0.9, make_chunk())]

    with pytest.raises(ValueError) as caught:
        cited_numbers("See [1] and [3].", hits)

    assert "3" in str(caught.value)


def test_citation_of_zero_is_rejected(make_chunk):
    with pytest.raises(ValueError):
        cited_numbers("See [0].", [Hit(0.9, make_chunk())])
