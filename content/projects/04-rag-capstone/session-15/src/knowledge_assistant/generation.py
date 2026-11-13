"""Generators: turn a question and numbered sources into a grounded answer.

Everything provider-specific stays in this module, as in Project 03. The rest of the
application depends on the Generator protocol, so tests and the offline mode can
substitute their own.
"""

import re
from dataclasses import dataclass
from typing import Protocol

import httpx2
import openai
from openai import OpenAI
from pydantic import BaseModel, PositiveFloat, PositiveInt, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from knowledge_assistant.errors import (
    GeneratorConfigurationError,
    GeneratorUnavailable,
    InvalidAnswerError,
)
from knowledge_assistant.prompts import ANSWER_INSTRUCTIONS
from knowledge_assistant.settings import Settings


class GroundedAnswer(BaseModel):
    """The model's output contract (structured output)."""

    answerable: bool
    answer: str
    citations: list[int]


@dataclass(frozen=True)
class Generation:
    result: GroundedAnswer
    model: str
    input_tokens: int = 0
    output_tokens: int = 0


class Generator(Protocol):
    model_id: str

    def generate(self, question: str, context: str) -> Generation: ...


class LLMSettings(BaseSettings):
    """LLM_MODEL, OPENAI_API_KEY ... : the course's variable names (Session 09)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", frozen=True)

    llm_model: str = "gpt-5.6-terra"
    openai_api_key: SecretStr | None = None
    openai_base_url: str | None = None  # None: the SDK's default, api.openai.com
    llm_timeout_seconds: PositiveFloat = 30.0
    llm_max_retries: int = 2
    llm_max_output_tokens: PositiveInt = 1000


def user_input(question: str, context: str) -> str:
    """What the model receives besides the instructions: the sources, then the question."""
    return f"Sources:\n\n{context}\n\nQuestion: {question}"


class OpenAIGenerator:
    """Answers with OpenAI's Responses API and structured outputs."""

    def __init__(self, client: OpenAI, *, model: str, max_output_tokens: int = 1000) -> None:
        self._client = client
        self.model_id = model
        self.max_output_tokens = max_output_tokens

    @classmethod
    def from_settings(
        cls, settings: LLMSettings, *, http_client: httpx2.Client | None = None
    ) -> "OpenAIGenerator":
        """A generator for the configured model. Fails fast, without a request, if no key."""
        if settings.openai_api_key is None:
            raise GeneratorConfigurationError("OPENAI_API_KEY is not set (add it to .env)")
        client = OpenAI(
            api_key=settings.openai_api_key.get_secret_value(),
            base_url=settings.openai_base_url,
            timeout=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
            http_client=http_client,
        )
        return cls(
            client, model=settings.llm_model, max_output_tokens=settings.llm_max_output_tokens
        )

    def generate(self, question: str, context: str) -> Generation:
        try:
            response = self._client.responses.parse(
                model=self.model_id,
                instructions=ANSWER_INSTRUCTIONS,
                input=user_input(question, context),
                text_format=GroundedAnswer,
                max_output_tokens=self.max_output_tokens,
            )
        except (openai.AuthenticationError, openai.PermissionDeniedError) as error:
            # The provider's message can echo part of the key, so it isn't repeated here.
            raise GeneratorConfigurationError(
                f"the provider rejected the API key ({error.status_code})"
            ) from error
        except openai.NotFoundError as error:
            raise GeneratorConfigurationError(
                f"model {self.model_id!r} was not found, or this key can't use it"
            ) from error
        except (
            openai.APIConnectionError,
            openai.RateLimitError,
            openai.InternalServerError,
        ) as error:
            raise GeneratorUnavailable(f"{type(error).__name__} after retries") from error
        except openai.APIStatusError as error:
            if error.status_code in (408, 409):
                raise GeneratorUnavailable(f"HTTP {error.status_code} after retries") from error
            raise GeneratorConfigurationError(
                f"the provider refused the request ({error.status_code})"
            ) from error
        except ValidationError as error:
            raise InvalidAnswerError("the model's output wasn't a valid answer") from error

        result = response.output_parsed
        if result is None:
            raise InvalidAnswerError("the model declined to answer, or returned nothing")
        usage = response.usage
        return Generation(
            result=result,
            model=response.model,
            input_tokens=usage.input_tokens if usage else 0,
            output_tokens=usage.output_tokens if usage else 0,
        )


class ExtractiveGenerator:
    """An offline stand-in for an LLM: free, instant, and not very clever.

    It "answers" with the opening of source [1], cited as [1]. That's enough to run the
    whole application, the API, the UI and the evaluation without a key. It can't tell
    whether source [1] actually answers the question: only retrieval's threshold decides
    what's found.
    """

    model_id = "extractive"

    def generate(self, question: str, context: str) -> Generation:
        blocks = re.split(r"\n\n(?=\[\d+\] \()", context.strip())
        first = blocks[0].split("\n", 1) if blocks and blocks[0] else []
        if len(first) < 2 or not first[1].strip():
            return Generation(
                GroundedAnswer(answerable=False, answer="", citations=[]), "extractive"
            )
        text = " ".join(first[1].split())
        if len(text) > 300:
            text = text[:300].rsplit(" ", 1)[0] + " ..."
        return Generation(
            GroundedAnswer(answerable=True, answer=f"{text} [1]", citations=[1]), "extractive"
        )


def make_generator(settings: Settings, *, http_client: httpx2.Client | None = None) -> Generator:
    if settings.generator == "extractive":
        return ExtractiveGenerator()
    return OpenAIGenerator.from_settings(LLMSettings(), http_client=http_client)
