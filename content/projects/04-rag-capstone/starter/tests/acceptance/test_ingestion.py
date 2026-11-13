"""Milestone 5: incremental, failure-tolerant ingestion. Do not edit."""

import logging
from dataclasses import replace

import pytest

from knowledge_assistant.errors import DocumentError, IndexMismatchError
from knowledge_assistant.ingestion import ingest
from knowledge_assistant.store import ChunkStore

CANARY = "CANARY-91d4 this sentence must never appear in a log"


def all_sources(docs):
    return sorted(
        path.relative_to(docs).as_posix()
        for path in docs.rglob("*")
        if path.suffix in (".md", ".pdf")
    )


# -- the first run, and the second ----------------------------------------------------------


def test_the_first_run_adds_every_document(docs, store, embedder):
    report = ingest(docs, store, embedder)
    assert report.added == all_sources(docs)
    assert report.updated == report.unchanged == report.removed == []
    assert report.failed == {}
    assert report.chunks_written == store.count() > 24
    assert sorted(store.sources()) == all_sources(docs)


def test_a_second_run_changes_nothing_and_embeds_nothing(docs, store, counting_embedder):
    ingest(docs, store, counting_embedder)
    before = {source: store.chunks(source) for source in store.sources()}
    calls = counting_embedder.calls

    report = ingest(docs, store, counting_embedder)

    assert report.unchanged == all_sources(docs)
    assert report.added == report.updated == report.removed == []
    assert report.chunks_written == 0
    assert counting_embedder.calls == calls  # not a single text embedded again
    assert {source: store.chunks(source) for source in store.sources()} == before


def test_stored_hashes_are_the_files_content_hashes(docs, store, embedder):
    from knowledge_assistant.documents import content_hash

    ingest(docs, store, embedder)
    path = docs / "guides" / "on-call-handbook.md"
    assert store.sources()["guides/on-call-handbook.md"] == content_hash(path)


# -- changes ------------------------------------------------------------------------------------


def test_an_edited_file_is_updated_and_only_it_is_embedded(docs, store, counting_embedder):
    ingest(docs, store, counting_embedder)
    path = docs / "runbooks" / "vpn-outage.md"
    path.write_text(
        path.read_text(encoding="utf-8") + "\n## Contacts\n\nCall the network desk.\n",
        encoding="utf-8",
    )
    counting_embedder.texts.clear()

    report = ingest(docs, store, counting_embedder)

    assert report.updated == ["runbooks/vpn-outage.md"]
    assert report.added == report.removed == []
    assert len(report.unchanged) == len(all_sources(docs)) - 1
    assert counting_embedder.texts  # something was embedded...
    assert all("VPN" in text for text in counting_embedder.texts)  # ...only from that file
    assert any(c.section == "Contacts" for c in store.chunks("runbooks/vpn-outage.md"))


def test_a_shorter_file_leaves_no_stale_chunks(docs, store, embedder):
    ingest(docs, store, embedder)
    path = docs / "runbooks" / "disk-space-alerts.md"
    path.write_text("# Runbook: Disk Space Alerts\n\nCall the platform team.\n", encoding="utf-8")

    ingest(docs, store, embedder)

    [chunk] = store.chunks("runbooks/disk-space-alerts.md")
    assert chunk.text == "Call the platform team."


def test_a_new_file_is_added(docs, store, embedder):
    ingest(docs, store, embedder)
    (docs / "guides" / "printer-jams.md").write_text(
        "# Guide: Printer Jams\n\n## Fix\n\nOpen tray 2.\n", encoding="utf-8"
    )
    report = ingest(docs, store, embedder)
    assert report.added == ["guides/printer-jams.md"]
    assert store.chunks("guides/printer-jams.md")[0].text == "Open tray 2."


def test_a_deleted_file_is_removed_from_the_index(docs, store, embedder):
    ingest(docs, store, embedder)
    (docs / "guides" / "phishing-response.md").unlink()
    report = ingest(docs, store, embedder)
    assert report.removed == ["guides/phishing-response.md"]
    assert "guides/phishing-response.md" not in store.sources()
    assert store.chunks("guides/phishing-response.md") == []


def test_a_renamed_file_is_removed_and_added(docs, store, embedder):
    ingest(docs, store, embedder)
    (docs / "runbooks" / "vpn-outage.md").rename(docs / "runbooks" / "office-vpn.md")
    report = ingest(docs, store, embedder)
    assert report.removed == ["runbooks/vpn-outage.md"]
    assert report.added == ["runbooks/office-vpn.md"]


# -- failures -------------------------------------------------------------------------------------


def test_broken_files_are_reported_and_the_rest_are_indexed(docs, store, embedder):
    (docs / "policies" / "broken.pdf").write_bytes(b"this is not a PDF\n" * 5)
    (docs / "guides" / "empty.md").write_bytes(b"")
    (docs / "guides" / "latin1.md").write_bytes("# Menü\n\nCafé".encode("latin-1"))
    (docs / "guides" / "title-only.md").write_text("# Only a title\n", encoding="utf-8")

    report = ingest(docs, store, embedder)

    broken = {"policies/broken.pdf", "guides/empty.md", "guides/latin1.md", "guides/title-only.md"}
    assert set(report.failed) == broken
    assert all(reason.strip() for reason in report.failed.values())
    assert not report.ok
    assert len(report.added) == 24
    assert broken.isdisjoint(store.sources())


def test_a_failed_file_is_retried_on_the_next_run(docs, store, embedder):
    path = docs / "guides" / "draft.md"
    path.write_bytes(b"")
    assert "guides/draft.md" in ingest(docs, store, embedder).failed
    path.write_text("# Draft\n\nFinished now.\n", encoding="utf-8")
    report = ingest(docs, store, embedder)
    assert report.added == ["guides/draft.md"]
    assert report.ok


def test_a_file_that_breaks_keeps_its_previous_chunks(docs, store, embedder):
    ingest(docs, store, embedder)
    source = "policies/on-call-rota.pdf"
    before = store.chunks(source)
    (docs / "policies" / "on-call-rota.pdf").write_bytes(b"%PDF-1.7\n")  # half-saved

    report = ingest(docs, store, embedder)

    assert source in report.failed
    assert source not in report.removed
    assert store.chunks(source) == before


def test_an_embedder_failure_stops_the_run_but_loses_nothing(
    docs, store, embedder, counting_embedder
):
    ingest(docs, store, embedder)
    for name in ("backup-failures.md", "vpn-outage.md"):
        path = docs / "runbooks" / name
        path.write_text(path.read_text(encoding="utf-8") + "\nRevised.\n", encoding="utf-8")
    vpn_before = store.chunks("runbooks/vpn-outage.md")
    counting_embedder.fail_on = "vpn-ber"  # the provider goes down mid-run

    with pytest.raises(RuntimeError):
        ingest(docs, store, counting_embedder)

    assert store.chunks("runbooks/vpn-outage.md") == vpn_before  # untouched, not half-done
    report = ingest(docs, store, embedder)  # the provider is back
    assert "runbooks/backup-failures.md" in report.unchanged  # finished before the failure
    assert report.updated == ["runbooks/vpn-outage.md"]


def test_a_missing_folder_is_an_error(tmp_path, store, embedder):
    with pytest.raises(DocumentError):
        ingest(tmp_path / "nowhere", store, embedder)


def test_an_embedder_that_does_not_match_the_index_is_refused(docs, index_dir, config, embedder):
    store = ChunkStore(index_dir, replace(config, embedding_model="hashing-256", dimensions=256))
    with pytest.raises(IndexMismatchError):
        ingest(docs, store, embedder)
    assert store.count() == 0


def test_changed_chunk_settings_take_effect_after_a_rebuild(docs, index_dir, config, embedder):
    ingest(docs, ChunkStore(index_dir, config), embedder)
    smaller = replace(config, chunk_size=200, chunk_overlap=20)
    with pytest.raises(IndexMismatchError):
        ChunkStore(index_dir, smaller)
    rebuilt = ChunkStore(index_dir, smaller, rebuild=True)
    report = ingest(docs, rebuilt, embedder)
    assert len(report.added) == 24
    assert all(
        len(chunk.text) <= 200 for source in rebuilt.sources() for chunk in rebuilt.chunks(source)
    )


# -- logging -------------------------------------------------------------------------------------


def test_logs_name_each_changed_and_failed_file(docs, store, embedder, caplog):
    caplog.set_level(logging.DEBUG)
    ingest(docs, store, embedder)
    (docs / "guides" / "phishing-response.md").unlink()
    path = docs / "runbooks" / "vpn-outage.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nRevised.\n", encoding="utf-8")
    (docs / "guides" / "empty.md").write_bytes(b"")
    caplog.clear()

    ingest(docs, store, embedder)

    messages = [(record.levelno, record.getMessage()) for record in caplog.records]
    assert any("runbooks/vpn-outage.md" in m for level, m in messages if level == logging.INFO)
    assert any("guides/phishing-response.md" in m for level, m in messages if level == logging.INFO)
    assert any("guides/empty.md" in m for level, m in messages if level == logging.WARNING)


def test_logs_never_contain_document_text_or_full_paths(docs, store, embedder, caplog):
    caplog.set_level(logging.DEBUG)
    (docs / "guides" / "canary.md").write_text(
        f"# Canary Guide\n\n## Body\n\n{CANARY}\n", encoding="utf-8"
    )
    (docs / "guides" / "canary-utf16.md").write_bytes(f"# Guide\n\n{CANARY}".encode("utf-16"))
    (docs / "policies" / "canary.pdf").write_bytes(f"%PDF-1.7\n{CANARY}\n".encode())

    ingest(docs, store, embedder)
    path = docs / "guides" / "canary.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nMore.\n", encoding="utf-8")
    ingest(docs, store, embedder)

    assert "guides/canary.md" in caplog.text
    assert "CANARY-91d4" not in caplog.text
    assert str(docs) not in caplog.text
