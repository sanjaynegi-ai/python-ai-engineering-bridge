"""Session 15, Milestone 2: from a question to a grounded answer. Do not edit."""

import logging

import pytest

from knowledge_assistant.answering import NOT_FOUND, answer_question, build_context, retrieve
from knowledge_assistant.errors import GeneratorUnavailable, InvalidAnswerError

QUESTION = "How do I promote the orders database replica?"


def ask(assistant, question=QUESTION):
    return answer_question(
        question,
        store=assistant.store,
        embedder=assistant.embedder,
        generator=assistant.generator,
        top_k=assistant.top_k,
        min_score=assistant.min_score,
    )


# -- retrieve and build_context ----------------------------------------------------------------


def test_retrieve_finds_the_failover_runbook_first(ingested, embedder):
    hits = retrieve(ingested, embedder, QUESTION, k=4, min_score=0.0)
    assert len(hits) == 4
    assert hits[0].chunk.source == "runbooks/database-failover.md"
    assert [hit.score for hit in hits] == sorted((hit.score for hit in hits), reverse=True)


def test_retrieve_drops_hits_below_the_threshold(ingested, embedder):
    everything = retrieve(ingested, embedder, QUESTION, k=10, min_score=-1.0)
    threshold = everything[2].score
    kept = retrieve(ingested, embedder, QUESTION, k=10, min_score=threshold)
    assert kept == [hit for hit in everything if hit.score >= threshold]
    assert retrieve(ingested, embedder, QUESTION, k=10, min_score=1.01) == []


@pytest.mark.parametrize("question", ["", "   ", "\n\t"])
def test_retrieve_rejects_a_blank_question(ingested, embedder, question):
    with pytest.raises(ValueError):
        retrieve(ingested, embedder, question, k=4, min_score=0.0)


def test_build_context_numbers_each_source_with_its_citation(make_hit):
    hits = [
        make_hit(0.9, "Promote db-03.", source="runbooks/db.md", section="Fail over"),
        make_hit(0.7, "P2: 24 hours.", source="policies/sla.pdf", section=None, page=1),
    ]
    assert build_context(hits) == (
        "[1] (runbooks/db.md, Fail over)\nPromote db-03.\n\n"
        "[2] (policies/sla.pdf, page 1)\nP2: 24 hours."
    )


# -- answers -------------------------------------------------------------------------------------


def test_an_answer_cites_the_sources_it_used(assistant, generator):
    generator.answer = "Run `promote-replica db-03` [1], after stopping writes [2]."
    generator.citations = [1, 2]

    answer = ask(assistant)

    assert answer.found
    assert answer.question == QUESTION
    assert answer.answer == generator.answer
    hits = retrieve(assistant.store, assistant.embedder, QUESTION, k=4, min_score=0.2)
    assert [s.number for s in answer.sources] == [1, 2]
    assert [s.source for s in answer.sources] == [hits[0].chunk.source, hits[1].chunk.source]
    assert answer.sources[0].citation == hits[0].chunk.citation
    assert answer.sources[0].score == pytest.approx(hits[0].score, abs=1e-3)
    assert answer.model == "scripted-model"
    assert (answer.input_tokens, answer.output_tokens) == (500, 40)


def test_only_cited_sources_are_returned_with_their_original_numbers(assistant, generator):
    generator.answer = "See the third source [3]."
    generator.citations = [3]
    answer = ask(assistant)
    assert [source.number for source in answer.sources] == [3]


def test_citations_in_the_text_count_even_if_the_list_misses_them(assistant, generator):
    generator.answer = "Stop writes first [2], then promote the replica [1]. Again [1]."
    generator.citations = [2]
    answer = ask(assistant)
    assert [source.number for source in answer.sources] == [1, 2]


def test_the_generator_receives_the_question_and_numbered_context(assistant, generator):
    ask(assistant, f"  {QUESTION}  ")
    [(question, context)] = generator.calls
    assert question == QUESTION
    hits = retrieve(assistant.store, assistant.embedder, QUESTION, k=4, min_score=0.2)
    assert context == build_context(hits)


# -- not found -----------------------------------------------------------------------------------


def test_nothing_retrieved_means_not_found_without_calling_the_model(assistant, generator):
    assistant.min_score = 1.01  # nothing can score this
    answer = ask(assistant)
    assert not answer.found
    assert answer.answer == NOT_FOUND
    assert answer.sources == []
    assert answer.model is None
    assert generator.calls == []  # no tokens spent on a question we can't answer


def test_the_model_saying_unanswerable_means_not_found(assistant, generator):
    generator.answerable = False
    generator.answer = ""
    generator.citations = []
    answer = ask(assistant, "What's on the cafeteria menu this week?")
    assert not answer.found
    assert answer.answer == NOT_FOUND
    assert answer.sources == []
    assert answer.model == "scripted-model"  # the model was called: its tokens count


# -- answers that can't be trusted --------------------------------------------------------------


def test_an_answer_without_citations_is_rejected(assistant, generator):
    generator.answer = "Promote the replica."
    generator.citations = []
    with pytest.raises(InvalidAnswerError):
        ask(assistant)


@pytest.mark.parametrize("bad", [0, 5, 99])
def test_a_citation_of_a_source_that_was_not_given_is_rejected(assistant, generator, bad):
    generator.answer = f"Promote the replica [{bad}]."
    generator.citations = [bad]
    with pytest.raises(InvalidAnswerError):
        ask(assistant)  # top_k is 4: only [1] to [4] exist


def test_generator_errors_pass_through(assistant, generator):
    generator.error = GeneratorUnavailable("timed out after retries")
    with pytest.raises(GeneratorUnavailable):
        ask(assistant)


# -- privacy -------------------------------------------------------------------------------------


def test_logs_never_contain_the_question_or_the_answer(assistant, generator, caplog):
    caplog.set_level(logging.DEBUG)
    generator.answer = "CANARY-ANSWER-4d2 promote it [1]."
    ask(assistant, f"{QUESTION} CANARY-QUESTION-8b1")
    assistant.min_score = 1.01
    ask(assistant, f"{QUESTION} CANARY-QUESTION-8b1")
    assert "CANARY" not in caplog.text
