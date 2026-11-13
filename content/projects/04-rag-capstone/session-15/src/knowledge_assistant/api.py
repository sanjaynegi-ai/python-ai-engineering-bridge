"""The HTTP API: a thin layer over the Assistant.

Run it with:  uv run uvicorn --factory knowledge_assistant.api:app_from_settings
"""

import logging

from fastapi import FastAPI, HTTPException  # noqa: F401

from knowledge_assistant.assistant import Assistant, build_assistant
from knowledge_assistant.errors import (  # noqa: F401
    GeneratorConfigurationError,
    GeneratorUnavailable,
    InvalidAnswerError,
)
from knowledge_assistant.schemas import Answer, AskRequest  # noqa: F401

logger = logging.getLogger(__name__)


def create_app(assistant: Assistant) -> FastAPI:
    """The API for `assistant`.

    GET /health -> {"status": "ok", "files": n, "chunks": m}
    POST /ask   -> Answer, for an AskRequest body. 422 for an invalid question; 503 if
                   the model is unavailable; 502 if its answer is unusable; 500 if the
                   generator is misconfigured. Error details are short messages, never
                   tracebacks or document text.
    """
    # TODO Milestone 3
    raise NotImplementedError


def app_from_settings() -> FastAPI:
    """The API for the assistant configured by the environment and .env."""
    return create_app(build_assistant())
