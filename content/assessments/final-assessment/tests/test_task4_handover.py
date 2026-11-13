"""Task 4: summarising a handover note. Do not edit."""

import httpx2
import pytest

from swap_desk.handover import (
    HANDOVER_INSTRUCTIONS,
    HandoverError,
    HandoverSummary,
    summarise_handover,
)

NOTE = "Berlin VPN still dropping (P2, network). db-03 promoted Saturday; no replica yet."


def test_a_valid_summary_is_returned(fake_openai):
    summary = summarise_handover(NOTE, client=fake_openai.client(), model="gpt-5.6-terra")
    assert isinstance(summary, HandoverSummary)
    assert summary.open_incidents == fake_openai.summary["open_incidents"]


def test_the_request_separates_instructions_from_the_note(fake_openai):
    summarise_handover(NOTE, client=fake_openai.client(), model="gpt-5.6-terra")
    [body] = fake_openai.bodies
    assert body["instructions"] == HANDOVER_INSTRUCTIONS
    assert body["input"] == NOTE
    assert body["model"] == "gpt-5.6-terra"
    assert body["text"]["format"]["type"] == "json_schema"


def test_a_blank_note_is_rejected_without_a_request(fake_openai):
    with pytest.raises(ValueError):
        summarise_handover("   ", client=fake_openai.client(), model="gpt-5.6-terra")
    assert fake_openai.requests == []


@pytest.mark.parametrize(
    "entry",
    [
        (503, {"error": {"message": "overloaded", "type": "server_error"}}),
        httpx2.ConnectError("connection refused"),
        "refusal",
        "invalid",
    ],
    ids=["server-error", "unreachable", "refusal", "invalid-output"],
)
def test_unusable_replies_are_handover_errors(fake_openai, entry):
    if entry == "refusal":
        entry = fake_openai.reply(refusal="I can't help with that.")
    elif entry == "invalid":
        entry = fake_openai.reply('{"open_incidents": "not a list"}')
    fake_openai.script = [entry]
    with pytest.raises(HandoverError):
        summarise_handover(NOTE, client=fake_openai.client(), model="gpt-5.6-terra")
