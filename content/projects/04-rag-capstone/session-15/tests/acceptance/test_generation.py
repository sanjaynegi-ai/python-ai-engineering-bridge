"""Session 15: the provided generators, checked against the fake API. Do not edit.

These tests cover code you were given, so they should pass as soon as you've copied the
Session 15 files and run `uv add`. If they fail, your setup is wrong, not your code.
"""

import httpx2
import pytest

from knowledge_assistant.errors import (
    GeneratorConfigurationError,
    GeneratorUnavailable,
    InvalidAnswerError,
)
from knowledge_assistant.generation import ExtractiveGenerator, LLMSettings, OpenAIGenerator

CONTEXT = (
    "[1] (runbooks/db.md, Fail over)\nPromote db-03.\n\n"
    "[2] (policies/sla.pdf, page 1)\nP2: 24 hours."
)
BAD_KEY = (401, {"error": {"message": "bad key", "type": "invalid_request_error"}})
OVERLOADED = (503, {"error": {"message": "overloaded", "type": "server_error"}})


@pytest.fixture
def openai_generator(fake_openai, clean_env):
    clean_env.setenv("OPENAI_API_KEY", "test-key-not-real")
    clean_env.setenv("LLM_MAX_RETRIES", "0")
    return OpenAIGenerator.from_settings(LLMSettings(), http_client=fake_openai.http_client())


def test_a_grounded_answer_is_parsed(openai_generator, fake_openai):
    fake_openai.script = [fake_openai.answer_reply("Promote db-03 [1].", [1])]
    generation = openai_generator.generate("How do I fail over?", CONTEXT)
    assert generation.result.answerable
    assert generation.result.citations == [1]
    assert generation.model == "gpt-5.6-terra"
    assert (generation.input_tokens, generation.output_tokens) == (900, 80)


def test_the_request_keeps_instructions_apart_from_the_sources(openai_generator, fake_openai):
    openai_generator.generate("How do I fail over?", CONTEXT)
    [body] = fake_openai.bodies
    assert "only the numbered sources" in body["instructions"]
    assert body["input"] == f"Sources:\n\n{CONTEXT}\n\nQuestion: How do I fail over?"
    assert body["text"]["format"]["type"] == "json_schema"


def test_no_key_fails_before_any_request(fake_openai, clean_env):
    with pytest.raises(GeneratorConfigurationError):
        OpenAIGenerator.from_settings(LLMSettings(), http_client=fake_openai.http_client())
    assert fake_openai.requests == []


@pytest.mark.parametrize(
    ("entry", "error"),
    [
        (BAD_KEY, GeneratorConfigurationError),
        (OVERLOADED, GeneratorUnavailable),
        (httpx2.ConnectError("refused"), GeneratorUnavailable),
    ],
)
def test_provider_errors_are_translated(openai_generator, fake_openai, entry, error):
    fake_openai.script = [entry]
    with pytest.raises(error):
        openai_generator.generate("q", CONTEXT)


@pytest.mark.parametrize(
    "reply",
    [
        {"kind": "refusal"},
        {"kind": "not json"},
    ],
)
def test_unusable_output_is_an_invalid_answer(openai_generator, fake_openai, reply):
    if reply["kind"] == "refusal":
        fake_openai.script = [fake_openai.reply(refusal="I can't help with that.")]
    else:
        fake_openai.script = [fake_openai.reply('{"answerable": tru')]
    with pytest.raises(InvalidAnswerError):
        openai_generator.generate("q", CONTEXT)


def test_the_extractive_generator_quotes_source_one():
    generation = ExtractiveGenerator().generate("How do I fail over?", CONTEXT)
    assert generation.result.answerable
    assert generation.result.answer == "Promote db-03. [1]"
    assert generation.result.citations == [1]


def test_the_extractive_generator_with_no_sources_is_unanswerable():
    assert not ExtractiveGenerator().generate("q", "").result.answerable
