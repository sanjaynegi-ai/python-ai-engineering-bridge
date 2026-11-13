"""Acceptance tests for evaluation and the command line (workbook Milestone 6). Do not edit."""

import json

import pytest

from handbook_search.chunking import chunk_documents
from handbook_search.cli import main
from handbook_search.evaluation import EvaluationQuestion, evaluate, load_questions
from handbook_search.loading import load_documents
from handbook_search.store import VectorStore


@pytest.fixture
def store(handbook, embedder) -> VectorStore:
    documents, _ = load_documents(handbook)
    chunks = chunk_documents(documents, size=500, overlap=100)
    store = VectorStore(embedder.model_id, embedder.dimensions)
    store.add(chunks, embedder.embed([c.embedding_text for c in chunks]))
    return store


def test_load_questions(tmp_path):
    path = tmp_path / "q.jsonl"
    lines = [
        {"question": "Where is X?", "expected_sources": ["x.md", "y.pdf"]},
        {"question": "Unknowable?", "expected_sources": []},
    ]
    path.write_text("\n".join(json.dumps(line) for line in lines) + "\n\n", encoding="utf-8")

    questions = load_questions(path)

    assert questions == [
        EvaluationQuestion("Where is X?", frozenset({"x.md", "y.pdf"})),
        EvaluationQuestion("Unknowable?", frozenset()),
    ]


def test_evaluate_counts_hits_and_misses(store, embedder):
    questions = [
        EvaluationQuestion(
            "promote the replica db-03", frozenset({"runbook-database-failover.md"})
        ),
        EvaluationQuestion(
            "rotate credentials every 90 days", frozenset({"policy-api-credentials.md"})
        ),
        EvaluationQuestion("promote the replica db-03", frozenset({"guide-phishing-response.md"})),
    ]

    result = evaluate(store, embedder, questions, k=1, min_score=0.0)

    assert (result.answerable, result.hits) == (3, 2)
    assert result.hit_rate == pytest.approx(2 / 3)
    assert result.misses == ["promote the replica db-03"]


def test_evaluate_counts_unanswerable_questions(store, embedder):
    questions = [
        EvaluationQuestion("cafeteria menu", frozenset()),
        EvaluationQuestion("promote the replica db-03", frozenset()),
    ]

    result = evaluate(store, embedder, questions, k=3, min_score=0.3)

    assert (result.unanswerable, result.correctly_empty) == (2, 1)
    assert result.rejection_rate == pytest.approx(0.5)
    assert result.misses == ["promote the replica db-03"]
    assert result.answerable == 0 and result.hit_rate == 0.0


@pytest.fixture
def project(clean_env, handbook, tmp_path):
    """A working folder with the handbook at the default location, and the hashing embedder."""
    (tmp_path / "data").mkdir()
    handbook.rename(tmp_path / "data" / "handbook")
    clean_env.setenv("HANDBOOK_EMBEDDER", "hashing")
    return tmp_path


def test_cli_ingest_writes_the_index(project, capsys):
    assert main(["ingest"]) == 0

    assert (project / "index" / "store.json").exists()
    out = capsys.readouterr().out
    assert "12 files" in out
    assert "hashing-512" in out


def test_cli_query_prints_numbered_sources(project, capsys):
    main(["ingest"])
    capsys.readouterr()
    project.joinpath(".env").write_text("HANDBOOK_MIN_SCORE=0.1\n", encoding="utf-8")

    assert main(["query", "promote the replica db-03"]) == 0

    out = capsys.readouterr().out
    assert out.startswith("[1] ")
    assert "runbook-database-failover.md" in out


def test_cli_query_with_nothing_relevant(project, capsys):
    main(["ingest"])
    capsys.readouterr()

    assert main(["query", "cafeteria menu"]) == 1
    assert "can't find this in the handbook" in capsys.readouterr().out


def test_cli_query_before_ingest(project, capsys):
    assert main(["query", "anything"]) == 2
    assert "ingest" in capsys.readouterr().err


def test_cli_ingest_reports_skipped_files(project, capsys):
    (project / "data" / "handbook" / "broken.md").write_bytes(b"\xff\xfe")

    assert main(["ingest"]) == 1
    assert "broken.md" in capsys.readouterr().err


def test_cli_evaluate(project, capsys):
    main(["ingest"])
    questions = project / "q.jsonl"
    questions.write_text(
        json.dumps({"question": "promote the replica db-03",
                    "expected_sources": ["runbook-database-failover.md"]}) + "\n",
        encoding="utf-8",
    )  # fmt: skip
    capsys.readouterr()
    project.joinpath(".env").write_text("HANDBOOK_MIN_SCORE=0.1\n", encoding="utf-8")

    assert main(["evaluate", str(questions)]) == 0
    assert "hit rate 100%" in capsys.readouterr().out


def test_cli_invalid_settings(project, capsys):
    project.joinpath(".env").write_text(
        "HANDBOOK_CHUNK_SIZE=100\nHANDBOOK_CHUNK_OVERLAP=200\n", encoding="utf-8"
    )

    assert main(["ingest"]) == 2
    assert "invalid settings" in capsys.readouterr().err


def test_cli_evaluate_with_a_miss(project, capsys):
    main(["ingest"])
    questions = project / "q.jsonl"
    line = {"question": "cafeteria menu", "expected_sources": ["runbook-vpn-outage.md"]}
    questions.write_text(json.dumps(line) + "\n", encoding="utf-8")
    capsys.readouterr()

    assert main(["evaluate", str(questions)]) == 1
    assert "cafeteria menu" in capsys.readouterr().out
