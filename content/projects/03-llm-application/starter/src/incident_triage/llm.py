"""The LLM behind a small interface: report in, validated triage out.

Everything provider-specific stays in this module. The rest of the application
depends on the Triager protocol, so tests (and Session 10's LangChain version)
can substitute their own implementation.
"""

from typing import Protocol

import httpx2
from openai import OpenAI

from incident_triage.models import IncidentReport, Triage
from incident_triage.settings import Settings


class Triager(Protocol):
    """Anything that can triage one report."""

    def triage(self, report: IncidentReport) -> Triage: ...


class OpenAITriager:
    """Triage with OpenAI's Responses API and structured outputs."""

    def __init__(self, client: OpenAI, *, model: str, max_output_tokens: int = 2000) -> None:
        self._client = client
        self.model = model
        self.max_output_tokens = max_output_tokens

    @classmethod
    def from_settings(
        cls, settings: Settings, *, http_client: httpx2.Client | None = None
    ) -> "OpenAITriager":
        """A triager for the configured model, using an OpenAI client built from the settings.

        Workbook Milestone 3. Raise LLMConfigurationError, without sending anything,
        if there's no API key. Pass http_client through to the OpenAI client: the tests
        use it to replace the network with a fake.
        """
        raise NotImplementedError

    def triage(self, report: IncidentReport) -> Triage:
        """Send one report; return a validated Triage, or raise a TriageError subclass.

        Workbook Milestone 3: the request, the result, and the error table.
        """
        raise NotImplementedError
