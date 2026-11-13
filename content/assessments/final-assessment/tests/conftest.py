"""Fixtures for the assessment's tests. Do not edit.

`fake_openai` stands in for OpenAI's Responses API at the HTTP level, as in Projects 03
and 04: no test makes a real API call.
"""

import json

import httpx2
import pytest


def response_body(output_text: str | None = None, *, refusal: str | None = None) -> dict:
    """A Responses API reply with one assistant message: text, or a refusal."""
    if refusal is not None:
        content = [{"type": "refusal", "refusal": refusal}]
    else:
        content = [{"type": "output_text", "text": output_text or "", "annotations": []}]
    return {
        "id": "resp_test_0001",
        "object": "response",
        "created_at": 1761120000,
        "model": "gpt-5.6-terra",
        "status": "completed",
        "incomplete_details": None,
        "error": None,
        "instructions": None,
        "metadata": {},
        "parallel_tool_calls": True,
        "temperature": None,
        "tool_choice": "auto",
        "tools": [],
        "top_p": None,
        "output": [
            {
                "type": "message",
                "id": "msg_test_0001",
                "role": "assistant",
                "status": "completed",
                "content": content,
            }
        ],
        "usage": {
            "input_tokens": 300,
            "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
            "output_tokens": 60,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": 360,
        },
    }


SUMMARY = {
    "open_incidents": ["P2: Berlin VPN drops every few minutes"],
    "risks": ["The orders database has no replica until Tuesday"],
    "summary": "One open P2, and the database cluster is running without a replica.",
}


class FakeOpenAI:
    """Replays scripted replies in order (the last one repeats) and records every request.

    Entries are a dict (a 200 reply), a (status, body) tuple, or an exception to raise.
    """

    reply = staticmethod(response_body)
    summary = SUMMARY

    def __init__(self) -> None:
        self.script: list = [response_body(json.dumps(SUMMARY))]
        self.requests: list[httpx2.Request] = []

    @property
    def bodies(self) -> list[dict]:
        return [json.loads(request.content) for request in self.requests]

    def handler(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(request)
        entry = self.script.pop(0) if len(self.script) > 1 else self.script[0]
        if isinstance(entry, Exception):
            raise entry
        if isinstance(entry, tuple):
            status, body = entry
            return httpx2.Response(status, json=body, headers={"retry-after-ms": "1"})
        return httpx2.Response(200, json=entry)

    def client(self):
        """An OpenAI client that talks to this fake, with retries switched off."""
        from openai import OpenAI

        return OpenAI(
            api_key="test-key-not-real",
            max_retries=0,
            http_client=httpx2.Client(transport=httpx2.MockTransport(self.handler)),
        )


@pytest.fixture
def fake_openai() -> FakeOpenAI:
    return FakeOpenAI()
