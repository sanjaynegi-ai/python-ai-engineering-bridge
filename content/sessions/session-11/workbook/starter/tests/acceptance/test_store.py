"""Acceptance tests for VectorStore (workbook Milestone 4). Do not edit."""

import json

import numpy as np
import pytest

from handbook_search.errors import SearchIndexError
from handbook_search.models import Hit
from handbook_search.store import VectorStore


@pytest.fixture
def store(make_chunk) -> VectorStore:
    store = VectorStore("test-model", 3)
    chunks = [
        make_chunk("north", source="a.md", index=0),
        make_chunk("east", source="a.md", index=1),
        make_chunk("north-east", source="b.md", index=0),
    ]
    vectors = np.array([[1, 0, 0], [0, 1, 0], [1, 1, 0]], dtype=np.float32)
    store.add(chunks, vectors)
    return store


def test_search_ranks_by_cosine_similarity(store):
    hits = store.search(np.array([1.0, 0.1, 0.0]), k=3)

    assert [h.chunk.text for h in hits] == ["north", "north-east", "east"]
    assert all(isinstance(h, Hit) for h in hits)
    assert hits[0].score == pytest.approx(0.995, abs=1e-3)


def test_vectors_are_normalised_when_added(store):
    hits = store.search(np.array([2.0, 2.0, 0.0]), k=1)  # a long query vector

    assert hits[0].chunk.text == "north-east"
    assert hits[0].score == pytest.approx(1.0, abs=1e-6)


def test_k_limits_the_results(store):
    assert len(store.search(np.array([1.0, 0.0, 0.0]), k=2)) == 2
    assert store.search(np.array([1.0, 0.0, 0.0]), k=0) == []


def test_min_score_drops_weak_results(store):
    hits = store.search(np.array([1.0, 0.0, 0.0]), k=3, min_score=0.5)

    assert [h.chunk.text for h in hits] == ["north", "north-east"]


def test_source_filter_is_applied_before_ranking(store):
    hits = store.search(np.array([1.0, 0.0, 0.0]), k=1, source="b.md")

    assert [h.chunk.text for h in hits] == ["north-east"]  # not an empty list


def test_empty_store_returns_nothing():
    assert VectorStore("m", 3).search(np.array([1.0, 0.0, 0.0])) == []


def test_len_and_chunks(store):
    assert len(store) == 3
    assert [c.text for c in store.chunks] == ["north", "east", "north-east"]


def test_add_rejects_mismatched_lengths(store, make_chunk):
    with pytest.raises(ValueError):
        store.add([make_chunk()], np.zeros((2, 3), dtype=np.float32))


def test_add_rejects_wrong_dimensions(store, make_chunk):
    with pytest.raises(ValueError):
        store.add([make_chunk()], np.zeros((1, 4), dtype=np.float32))


def test_search_rejects_wrong_query_dimensions(store):
    with pytest.raises(ValueError):
        store.search(np.array([1.0, 0.0]))


def test_save_and_load_round_trip(store, tmp_path):
    store.save(tmp_path / "index")

    loaded = VectorStore.load(tmp_path / "index", model_id="test-model")

    query = np.array([0.2, 1.0, 0.0])
    assert [h.chunk for h in loaded.search(query)] == [h.chunk for h in store.search(query)]
    assert sorted(p.name for p in (tmp_path / "index").iterdir()) == ["store.json", "vectors.npy"]


def test_the_saved_metadata_is_readable_json(store, tmp_path):
    store.save(tmp_path / "index")

    meta = json.loads((tmp_path / "index" / "store.json").read_text(encoding="utf-8"))

    assert meta["model_id"] == "test-model"
    assert meta["dimensions"] == 3
    assert meta["chunks"][0]["source"] == "a.md"


def test_load_refuses_a_different_model(store, tmp_path):
    store.save(tmp_path / "index")

    with pytest.raises(SearchIndexError) as caught:
        VectorStore.load(tmp_path / "index", model_id="another-model")

    assert "test-model" in str(caught.value)


def test_load_without_an_index(tmp_path):
    with pytest.raises(SearchIndexError):
        VectorStore.load(tmp_path / "nothing-here", model_id="test-model")


def test_load_a_damaged_index(store, tmp_path):
    store.save(tmp_path / "index")
    (tmp_path / "index" / "store.json").write_text("{not json", encoding="utf-8")

    with pytest.raises(SearchIndexError):
        VectorStore.load(tmp_path / "index", model_id="test-model")


def test_load_an_index_whose_files_disagree(store, tmp_path):
    store.save(tmp_path / "index")
    np.save(tmp_path / "index" / "vectors.npy", np.zeros((2, 3), dtype=np.float32))

    with pytest.raises(SearchIndexError):
        VectorStore.load(tmp_path / "index", model_id="test-model")
