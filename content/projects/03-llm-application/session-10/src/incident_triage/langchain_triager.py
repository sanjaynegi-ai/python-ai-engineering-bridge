"""Triage with LangChain: the same Triager protocol, built from a prompt, a chat model and
structured output. Compare it with llm.py, the direct-SDK version from Session 09.

Session 10 workbook, Milestones 2 and 3.
"""

import httpx2
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from incident_triage.models import IncidentReport, Triage
from incident_triage.settings import Settings

# Milestone 2: a prompt with two messages, the instructions (TRIAGE_INSTRUCTIONS) as the
# system message and the report as the human message, with one variable: {report}.
PROMPT: ChatPromptTemplate


class LangChainTriager:
    """Triage through a LangChain chain: PROMPT | model.with_structured_output(TriageResult)."""

    def __init__(self, model: BaseChatModel) -> None:
        """Keep the model as self.model, and build the chain as self.chain (a Runnable).

        Use include_raw=True: the raw message carries the token usage and any refusal.
        """
        self.model = model
        self.chain: Runnable
        raise NotImplementedError

    @classmethod
    def from_settings(
        cls, settings: Settings, *, http_client: httpx2.Client | None = None
    ) -> "LangChainTriager":
        """A triager whose model is a ChatOpenAI configured from the settings.

        The same configuration as OpenAITriager.from_settings: key, base URL, model,
        timeout, retries and output token limit, with OpenAI's Responses API. Raise
        LLMConfigurationError, without sending anything, if there's no key.
        """
        raise NotImplementedError

    def triage(self, report: IncidentReport) -> Triage:
        """The same contract as OpenAITriager.triage: a validated Triage, or a TriageError."""
        raise NotImplementedError
