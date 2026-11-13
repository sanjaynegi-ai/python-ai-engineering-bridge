"""Session 15, Milestone 5: evaluation. Do not edit."""

import json
from pathlib import Path

import pytest

from knowledge_assistant.errors import GeneratorUnavailable
from knowledge_assistant.evaluation import EvalQuestion, evaluate, load_questions

QUESTIONS = Path(__file__).parents[2] / "data" / "eval" / "questions.jsonl"
FAILOVER = "How do I promote the orders database replica?"
CAFETERIA = "What's on the cafeteria menu this week?"


def q(question: str, *sources: str) -> EvalQuestion:
    return EvalQuestion(question, frozenset(sources))


def test_load_questions_reads_the_sample_set():
    questions = load_questions(QUESTIONS)
    assert len(questions) == 20
    assert sum(item.answerable for item in questions) == 16
    assert questions[0] == q(FAILOVER, "runbooks/database-failover.md")


def test_load_questions_skips_blank_lines(tmp_path):
    path = tmp_path / "q.jsonl"
    lines = [
        json.dumps({"question": "A?", "expected_sources": ["a.md"]}),
        "",
        "  ",
        json.dumps({"question": "B?", "expected_sources": []}),
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert load_questions(path) == [q("A?", "a.md"), q("B?")]


def test_every_expected_source_exists_in_the_documents(docs):
    from knowledge_assistant.documents import discover

    sources = set(discover(docs))
    for item in load_questions(QUESTIONS):
        assert item.expected_sources <= sources, item.question


def test_a_found_and_correctly_cited_answer_counts_everywhere(assistant, generator):
    report = evaluate(assistant, [q(FAILOVER, "runbooks/database-failover.md")])
    [result] = report.results
    assert result.retrieved[0] == "runbooks/database-failover.md"
    assert result.found
    assert result.cited == ["runbooks/database-failover.md"]
    assert result.retrieval_hit and result.grounded
    assert report.retrieval_hit_rate == report.answer_rate == report.grounded_rate == 1.0


def test_citing_the_wrong_source_is_retrieved_but_not_grounded(assistant, generator):
    from knowledge_assistant.answering import retrieve

    hits = retrieve(assistant.store, assistant.embedder, FAILOVER, k=4, min_score=0.2)
    other = next(n for n, hit in enumerate(hits, 1) if "failover" not in hit.chunk.source)
    generator.answer = f"See [{other}]."
    generator.citations = [other]
    report = evaluate(assistant, [q(FAILOVER, "runbooks/database-failover.md")])
    [result] = report.results
    assert result.retrieval_hit
    assert result.cited and result.cited[0] != "runbooks/database-failover.md"
    assert not result.grounded
    assert report.answer_rate == 1.0
    assert report.grounded_rate == 0.0


def test_unanswerable_questions_count_only_when_declined(assistant, generator):
    generator.answerable = False
    generator.citations = []
    generator.answer = ""
    report = evaluate(assistant, [q(CAFETERIA), q(FAILOVER, "runbooks/database-failover.md")])
    assert report.rejection_rate == 1.0
    assert report.answer_rate == 0.0
    assert report.retrieval_hit_rate == 1.0  # retrieval worked; the model declined


def test_answering_an_unanswerable_question_is_a_miss(assistant):
    report = evaluate(assistant, [q(CAFETERIA)])
    [result] = report.results
    assert result.found
    assert not result.correctly_rejected
    assert report.rejection_rate == 0.0


def test_rates_are_fractions_of_the_right_group(assistant, generator):
    questions = [
        q(FAILOVER, "runbooks/database-failover.md"),
        q("How long are application logs kept?", "policies/does-not-exist.md"),
        q(CAFETERIA),
        q("What will the weather be in Zurich tomorrow?"),
    ]
    report = evaluate(assistant, questions)
    assert len(report.answerable) == 2 and len(report.unanswerable) == 2
    assert report.retrieval_hit_rate == 0.5
    assert report.grounded_rate == 0.5
    assert report.rejection_rate == 0.0  # the scripted model answers everything


def test_a_generation_error_is_recorded_and_the_run_carries_on(assistant, generator):
    generator.error = GeneratorUnavailable("timed out after retries")
    report = evaluate(assistant, [q(FAILOVER, "runbooks/database-failover.md"), q(CAFETERIA)])
    assert report.errors == 2
    assert all(result.error for result in report.results)
    assert report.answer_rate == 0.0
    assert report.rejection_rate == 0.0  # an error is not a correct "not found"
    assert report.retrieval_hit_rate == 1.0  # retrieval still happened


def test_empty_groups_give_zero_rates_not_errors(assistant):
    report = evaluate(assistant, [])
    assert report.results == []
    assert (report.retrieval_hit_rate, report.rejection_rate) == (0.0, 0.0)


@pytest.mark.parametrize("k", [1, 4])
def test_the_sample_set_runs_end_to_end_offline(ingested, embedder, k):
    from knowledge_assistant.assistant import Assistant
    from knowledge_assistant.generation import ExtractiveGenerator

    assistant = Assistant(ingested, embedder, ExtractiveGenerator(), top_k=k, min_score=0.2)
    report = evaluate(assistant, load_questions(QUESTIONS))
    assert len(report.results) == 20
    assert report.errors == 0
    assert all(len(result.retrieved) <= k for result in report.results)
    assert 0.5 <= report.retrieval_hit_rate <= 1.0
