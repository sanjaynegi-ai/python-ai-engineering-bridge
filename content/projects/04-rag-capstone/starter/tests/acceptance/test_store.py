"""Milestone 4: the persistent index. Do not edit."""

from dataclasses import replace

import numpy as np
import pytest

from knowledge_assistant.errors import IndexMismatchError
from knowledge_assistant.store import ChunkStore


def chunks_for(make_chunk, source: str, texts: list[str], content_hash: str = "a" * 64):
    return [
        make_chunk(text, source=source, index=i, content_hash=content_hash)
        for i, text in enumerate(texts)
    ]


def put(store, embedder, chunks):
    store.replace(chunks[0].source, chunks, embedder.embed([c.embedding_text for c in chunks]))


def test_a_new_store_is_empty(store):
    assert store.count() == 0
    assert store.sources() == {}
    assert store.chunks("runbooks/example.md") == []


def test_replace_stores_chunks_with_all_their_metadata(store, embedder, make_chunk):
    chunks = [
        make_chunk("Markdown text.", source="a.md", index=0, section="Fix", page=None),
        make_chunk("More text.", source="a.md", index=1, section=None, page=None),
    ]
    put(store, embedder, chunks)
    assert store.count() == 2
    assert store.chunks("a.md") == chunks  # None fields come back as None


def test_pdf_chunks_keep_their_page_numbers(store, embedder, make_chunk):
    chunks = [
        make_chunk("Page one.", source="p.pdf", index=0, section=None, page=1),
        make_chunk("Page two.", source="p.pdf", index=1, section=None, page=2),
    ]
    put(store, embedder, chunks)
    assert [chunk.page for chunk in store.chunks("p.pdf")] == [1, 2]


def test_sources_maps_each_source_to_its_content_hash(store, embedder, make_chunk):
    put(store, embedder, chunks_for(make_chunk, "b.md", ["one", "two"], "b" * 64))
    put(store, embedder, chunks_for(make_chunk, "a.md", ["three"], "c" * 64))
    assert store.sources() == {"a.md": "c" * 64, "b.md": "b" * 64}


def test_replace_with_fewer_chunks_leaves_no_old_ones_behind(store, embedder, make_chunk):
    put(store, embedder, chunks_for(make_chunk, "a.md", ["one", "two", "three", "four"]))
    shorter = chunks_for(make_chunk, "a.md", ["uno", "dos"], "d" * 64)
    put(store, embedder, shorter)
    assert store.count() == 2
    assert store.chunks("a.md") == shorter
    assert store.sources() == {"a.md": "d" * 64}


def test_replace_does_not_touch_other_sources(store, embedder, make_chunk):
    other = chunks_for(make_chunk, "other.md", ["keep me"])
    put(store, embedder, other)
    put(store, embedder, chunks_for(make_chunk, "a.md", ["one", "two"]))
    put(store, embedder, chunks_for(make_chunk, "a.md", ["only"]))
    assert store.chunks("other.md") == other
    assert store.count() == 2


def test_replace_with_no_chunks_removes_the_source(store, embedder, make_chunk):
    put(store, embedder, chunks_for(make_chunk, "a.md", ["one", "two"]))
    store.replace("a.md", [], np.empty((0, embedder.dimensions), dtype=np.float32))
    assert store.sources() == {}


def test_replace_rejects_bad_input_before_changing_anything(store, embedder, make_chunk):
    original = chunks_for(make_chunk, "a.md", ["one", "two"])
    put(store, embedder, original)
    new = chunks_for(make_chunk, "a.md", ["x", "y"], "e" * 64)
    vectors = embedder.embed([c.embedding_text for c in new])
    with pytest.raises(ValueError):
        store.replace("a.md", new, vectors[:1])  # one vector for two chunks
    with pytest.raises(ValueError):
        store.replace("a.md", new, np.ones((2, embedder.dimensions + 1), dtype=np.float32))
    with pytest.raises(ValueError):
        store.replace("a.md", [replace(new[0], source="b.md"), new[1]], vectors)
    assert store.chunks("a.md") == original


def test_remove_deletes_one_source_and_counts_its_chunks(store, embedder, make_chunk):
    put(store, embedder, chunks_for(make_chunk, "a.md", ["one", "two", "three"]))
    put(store, embedder, chunks_for(make_chunk, "b.md", ["four"]))
    assert store.remove("a.md") == 3
    assert store.sources().keys() == {"b.md"}
    assert store.remove("a.md") == 0


def test_the_index_survives_reopening(index_dir, config, embedder, make_chunk):
    chunks = chunks_for(make_chunk, "a.md", ["persist me", "and me"])
    put(ChunkStore(index_dir, config), embedder, chunks)
    reopened = ChunkStore(index_dir, config)
    assert reopened.count() == 2
    assert reopened.chunks("a.md") == chunks


@pytest.mark.parametrize(
    "change",
    [
        {"embedding_model": "another-model"},
        {"chunk_size": 500},
        {"chunk_overlap": 0},
    ],
)
def test_reopening_with_other_settings_is_refused(index_dir, config, change):
    ChunkStore(index_dir, config)
    with pytest.raises(IndexMismatchError, match=next(iter(change))):
        ChunkStore(index_dir, replace(config, **change))


def test_rebuild_starts_an_empty_index_with_the_new_settings(
    index_dir, config, embedder, make_chunk
):
    put(ChunkStore(index_dir, config), embedder, chunks_for(make_chunk, "a.md", ["old"]))
    smaller = replace(config, chunk_size=500)
    rebuilt = ChunkStore(index_dir, smaller, rebuild=True)
    assert rebuilt.count() == 0
    assert ChunkStore(index_dir, smaller).count() == 0  # the new settings were recorded


def test_search_returns_the_closest_chunks_best_first(store, embedder, make_chunk):
    texts = [
        "Promote the database replica with the promotion job.",
        "Reset your password if you typed it into a phishing page.",
        "Switch the office to the backup internet link.",
    ]
    put(store, embedder, chunks_for(make_chunk, "a.md", texts))
    hits = store.search(embedder.embed(["promote the replica database"])[0], k=2)
    assert len(hits) == 2
    assert hits[0].chunk.text == texts[0]
    assert hits[0].score >= hits[1].score
    assert hits[0].score == pytest.approx(
        float(
            embedder.embed([hits[0].chunk.embedding_text])[0]
            @ embedder.embed(["promote the replica database"])[0]
        ),
        abs=1e-4,
    )


def test_search_with_k_larger_than_the_index_returns_everything(store, embedder, make_chunk):
    put(store, embedder, chunks_for(make_chunk, "a.md", ["one", "two"]))
    assert len(store.search(embedder.embed(["one"])[0], k=10)) == 2


def test_search_on_an_empty_index_finds_nothing(store, embedder):
    assert store.search(embedder.embed(["anything"])[0], k=3) == []
