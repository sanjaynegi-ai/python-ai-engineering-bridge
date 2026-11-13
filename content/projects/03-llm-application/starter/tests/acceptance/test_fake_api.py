"""Contract tests for the test fakes themselves. Do not edit.

A fake that drifts away from the real API makes every test that uses it worthless.
These tests check the fake replies against the OpenAI SDK's own types, with strict
validation, so an SDK upgrade that changes the shape is noticed here first.
"""

from openai.types.responses import Response


def test_triage_reply_matches_the_sdk_response_type(fake_openai):
    response = Response.model_validate(fake_openai.triage_reply())

    assert response.output_text.startswith("{")
    assert response.usage.input_tokens == 420


def test_refusal_reply_matches_the_sdk_response_type(fake_openai):
    response = Response.model_validate(fake_openai.reply(refusal="I can't help with that."))

    assert response.output[0].content[0].type == "refusal"


def test_incomplete_reply_matches_the_sdk_response_type(fake_openai):
    body = fake_openai.reply(
        '{"priority": "P2", "sum', status="incomplete", incomplete_reason="max_output_tokens"
    )

    response = Response.model_validate(body)

    assert response.status == "incomplete"
    assert response.incomplete_details.reason == "max_output_tokens"
