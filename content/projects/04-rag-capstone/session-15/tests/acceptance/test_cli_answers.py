"""Session 15, Milestone 6: asking and evaluating through the provided CLI. Do not edit."""

import pytest

from knowledge_assistant.cli import main


@pytest.fixture
def env(clean_env, docs, tmp_path):
    """The CLI on a private index, with the hashing embedder and the offline generator."""
    clean_env.setenv("ASSISTANT_DOCUMENTS", str(docs))
    clean_env.setenv("ASSISTANT_INDEX", str(tmp_path / "index"))
    clean_env.setenv("ASSISTANT_EMBEDDER", "hashing")
    clean_env.setenv("ASSISTANT_GENERATOR", "extractive")
    assert main(["ingest"]) == 0
    return clean_env


def test_ask_prints_the_answer_and_its_sources(env, capsys):
    capsys.readouterr()
    assert main(["ask", "How do I promote the orders database replica?"]) == 0
    out = capsys.readouterr().out
    assert "[1]" in out
    assert "runbooks/database-failover.md" in out


def test_ask_exits_1_when_not_found(env, capsys):
    env.setenv("ASSISTANT_MIN_SCORE", "1.0")
    assert main(["ask", "What's on the cafeteria menu?"]) == 1
    assert "can't find" in capsys.readouterr().out


def test_ask_without_a_key_exits_2(env, capsys):
    env.setenv("ASSISTANT_GENERATOR", "openai")
    assert main(["ask", "How do I promote the orders database replica?"]) == 2
    assert "OPENAI_API_KEY" in capsys.readouterr().err


def test_evaluate_prints_the_four_rates(env, capsys, docs):
    from pathlib import Path

    questions = Path(__file__).parents[2] / "data" / "eval" / "questions.jsonl"
    capsys.readouterr()
    assert main(["evaluate", str(questions)]) == 0
    out = capsys.readouterr().out
    for line in ("retrieval hit rate", "answer rate", "grounded rate", "rejection rate"):
        assert line in out
    assert "20 questions" in out
