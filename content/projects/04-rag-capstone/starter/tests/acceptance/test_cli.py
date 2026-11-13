"""Milestone 6: the whole pipeline through the provided command line. Do not edit."""

import pytest

from knowledge_assistant.cli import main


@pytest.fixture
def env(clean_env, docs, tmp_path):
    """The CLI pointed at a private copy of the documents, with the hashing embedder."""
    clean_env.setenv("ASSISTANT_DOCUMENTS", str(docs))
    clean_env.setenv("ASSISTANT_INDEX", str(tmp_path / "index"))
    clean_env.setenv("ASSISTANT_EMBEDDER", "hashing")
    return clean_env


def test_ingest_twice(env, capsys):
    assert main(["ingest"]) == 0
    first = capsys.readouterr().out
    assert "24 added" in first
    assert main(["ingest"]) == 0
    assert "24 unchanged" in capsys.readouterr().out


def test_ingest_reports_failures_with_exit_code_1(env, docs, capsys):
    (docs / "policies" / "broken.pdf").write_bytes(b"not a pdf")
    assert main(["ingest"]) == 1
    captured = capsys.readouterr()
    assert "policies/broken.pdf" in captured.err
    assert "1 failed" in captured.out


def test_changing_the_chunk_size_needs_a_rebuild(env, capsys):
    assert main(["ingest"]) == 0
    env.setenv("ASSISTANT_CHUNK_SIZE", "300")
    assert main(["ingest"]) == 2
    assert "--rebuild" in capsys.readouterr().err
    assert main(["ingest", "--rebuild"]) == 0
    assert "24 added" in capsys.readouterr().out


def test_status_lists_the_indexed_files(env, capsys):
    assert main(["status"]) == 1  # empty
    main(["ingest"])
    capsys.readouterr()
    assert main(["status"]) == 0
    out = capsys.readouterr().out
    assert "runbooks/database-failover.md" in out
    assert "policies/on-call-rota.pdf" in out


def test_search_finds_the_failover_runbook(env, capsys):
    main(["ingest"])
    capsys.readouterr()
    assert main(["search", "How do I promote the orders database replica?"]) == 0
    first_line = capsys.readouterr().out.splitlines()[0]
    assert "runbooks/database-failover.md" in first_line


def test_a_missing_documents_folder_exits_2(env, tmp_path, capsys):
    env.setenv("ASSISTANT_DOCUMENTS", str(tmp_path / "nowhere"))
    assert main(["ingest"]) == 2
    assert "nowhere" in capsys.readouterr().err
