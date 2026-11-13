"""Session 16, Milestone 2: the whole assistant, end to end. Do not edit.

Unit and acceptance tests check one module at a time, often with fakes. These tests
wire the real pieces together the way a user meets them: the CLI builds the index on a
copy of the documents, the API answers from it, the documents change, and the answers
follow. Only the embedding model (hashing) and the LLM (the offline extractive
generator) are stand-ins, so no download or key is needed.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from knowledge_assistant.assistant import build_assistant
from knowledge_assistant.cli import main
from knowledge_assistant.settings import Settings

FAILOVER = "How do I promote the orders database replica?"
EMERGENCY = "Who approves an emergency change?"


@pytest.fixture
def env(clean_env, docs, tmp_path):
    clean_env.setenv("ASSISTANT_DOCUMENTS", str(docs))
    clean_env.setenv("ASSISTANT_INDEX", str(tmp_path / "index"))
    clean_env.setenv("ASSISTANT_EMBEDDER", "hashing")
    clean_env.setenv("ASSISTANT_GENERATOR", "extractive")
    return clean_env


def api() -> TestClient:
    """A fresh API over the current index, as a restarted service would see it."""
    from knowledge_assistant.api import create_app

    return TestClient(create_app(build_assistant(Settings())))


def ask(client: TestClient, question: str) -> dict:
    response = client.post("/ask", json={"question": question})
    assert response.status_code == 200, response.text
    return response.json()


def cited(answer: dict) -> set[str]:
    return {source["source"] for source in answer["sources"]}


def test_ingest_then_ask_through_the_api(env):
    assert main(["ingest"]) == 0
    client = api()
    assert client.get("/health").json()["files"] == 24
    answer = ask(client, FAILOVER)
    assert answer["found"]
    assert "runbooks/database-failover.md" in cited(answer)


def test_an_edited_runbook_is_answered_from_its_new_text(env, docs):
    main(["ingest"])
    (docs / "runbooks" / "database-failover.md").write_text(
        "# Runbook: Orders Database Failover\n\n## Fail over\n\n"
        "Promote the orders database replica with promote-replica db-07 "
        "from the automation tool.\n",
        encoding="utf-8",
    )
    assert main(["ingest"]) == 0
    answer = ask(api(), FAILOVER)
    assert cited(answer) == {"runbooks/database-failover.md"}
    assert "db-07" in answer["answer"]
    assert "db-03" not in answer["answer"]


def test_a_deleted_policy_is_never_cited_again(env, docs):
    main(["ingest"])
    assert "policies/change-management.md" in cited(ask(api(), EMERGENCY))
    (docs / "policies" / "change-management.md").unlink()
    main(["ingest"])
    assert "policies/change-management.md" not in cited(ask(api(), EMERGENCY))


def test_a_broken_document_does_not_stop_the_assistant(env, docs):
    (docs / "policies" / "half-uploaded.pdf").write_bytes(b"%PDF-1.7\n")
    assert main(["ingest"]) == 1  # reported...
    client = api()
    assert client.get("/health").json()["files"] == 24  # ...and everything else indexed
    assert ask(client, FAILOVER)["found"]


def test_the_cli_and_the_api_give_the_same_answer(env, capsys):
    main(["ingest"])
    capsys.readouterr()
    assert main(["ask", FAILOVER]) == 0
    printed = capsys.readouterr().out
    assert ask(api(), FAILOVER)["answer"] in printed


def test_the_evaluation_runs_on_a_freshly_built_index(env, capsys):
    main(["ingest"])
    capsys.readouterr()
    questions = Path(__file__).parents[2] / "data" / "eval" / "questions.jsonl"
    assert main(["evaluate", str(questions)]) == 0
    assert "20 questions" in capsys.readouterr().out


def test_an_index_built_with_other_settings_stops_the_service_at_startup(env):
    main(["ingest"])
    env.setenv("ASSISTANT_CHUNK_SIZE", "300")
    from knowledge_assistant.errors import IndexMismatchError

    with pytest.raises(IndexMismatchError):
        build_assistant(Settings())
