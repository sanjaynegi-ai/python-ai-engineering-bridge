"""Fixtures shared by every test. Do not edit.

No test makes a real API call. `fake_openai` stands in for OpenAI's Responses API at
the HTTP level: the real SDK builds and sends each request to an httpx2.MockTransport,
which replies with JSON in the API's documented shape (checked against the SDK's own
`Response` type by test_fixtures.py).
"""

import json
import os
from collections.abc import Callable

import httpx2
import pytest

VALID_TRIAGE = {
    "priority": "P2",
    "team": "network",
    "category": "degradation",
    "affected_system": "Berlin office VPN",
    "summary": "VPN connections in the Berlin office drop every few minutes.",
    "tags": ["vpn", "berlin"],
}


def response_body(
    output_text: str | None = None,
    *,
    refusal: str | None = None,
    status: str = "completed",
    incomplete_reason: str | None = None,
    model: str = "gpt-5.6-terra",
    input_tokens: int = 420,
    output_tokens: int = 60,
) -> dict:
    """A Responses API reply with one assistant message: text, or a refusal."""
    if refusal is not None:
        content = [{"type": "refusal", "refusal": refusal}]
    else:
        content = [{"type": "output_text", "text": output_text or "", "annotations": []}]
    return {
        "id": "resp_test_0001",
        "object": "response",
        "created_at": 1761120000,
        "model": model,
        "status": status,
        "incomplete_details": {"reason": incomplete_reason} if incomplete_reason else None,
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
                "status": status,
                "content": content,
            }
        ],
        "usage": {
            "input_tokens": input_tokens,
            "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
            "output_tokens": output_tokens,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": input_tokens + output_tokens,
        },
    }


def triage_body(**overrides) -> dict:
    """A successful reply whose text is a triage, with any fields overridden."""
    return response_body(json.dumps(VALID_TRIAGE | overrides))


def error_body(status: int, message: str, code: str | None = None) -> dict:
    return {"error": {"message": message, "type": "invalid_request_error", "code": code}}


class FakeOpenAI:
    """Replays scripted replies, in order, and records every request the SDK sends.

    Script entries are a dict (a 200 reply), a (status, body) tuple, or an exception
    instance to raise, such as httpx2.ReadTimeout. When the script runs out, the
    last entry repeats, which is what retries see.
    """

    # Reply builders, for tests: fake_openai.triage_reply(priority="P1") and so on
    reply = staticmethod(response_body)
    triage_reply = staticmethod(triage_body)
    error_reply = staticmethod(error_body)
    valid_triage = VALID_TRIAGE

    def __init__(self) -> None:
        self.script: list[dict | tuple[int, dict] | Exception] = [triage_body()]
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

    def http_client(self) -> httpx2.Client:
        return httpx2.Client(transport=httpx2.MockTransport(self.handler))


@pytest.fixture
def fake_openai() -> FakeOpenAI:
    return FakeOpenAI()


@pytest.fixture
def clean_env(monkeypatch, tmp_path):
    """No LLM or provider variables, and an empty working folder, so no real .env is read."""
    for name in list(os.environ):
        if name.upper().startswith(("LLM_", "OPENAI_", "ANTHROPIC_", "OPENROUTER_")):
            monkeypatch.delenv(name)
    monkeypatch.chdir(tmp_path)
    return monkeypatch


@pytest.fixture
def make_report() -> Callable:
    from incident_triage.models import IncidentReport

    def _make_report(report_id: str = "RPT-1003", text: str | None = None) -> IncidentReport:
        return IncidentReport(
            id=report_id,
            text=text or "VPN keeps dropping every few minutes for everyone in the Berlin office.",
        )

    return _make_report
