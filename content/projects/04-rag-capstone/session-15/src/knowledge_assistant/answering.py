"""From a question to a grounded answer: retrieve, build the context, generate, cite."""

import logging
import re  # noqa: F401  (useful for finding [n] in an answer)

from knowledge_assistant.embedding import Embedder
from knowledge_assistant.errors import InvalidAnswerError  # noqa: F401
from knowledge_assistant.generation import Generator
from knowledge_assistant.models import Hit
from knowledge_assistant.schemas import Answer, SourceRef  # noqa: F401
from knowledge_assistant.store import ChunkStore

logger = logging.getLogger(__name__)

NOT_FOUND = "I can't find this in the documentation."


def retrieve(
    store: ChunkStore, embedder: Embedder, question: str, *, k: int, min_score: float
) -> list[Hit]:
    """The best `k` chunks for `question` that score at least `min_score`, best first.

    Raises ValueError for a blank question.
    """
    # TODO Milestone 2
    raise NotImplementedError


def build_context(hits: list[Hit]) -> str:
    """Numbered sources for the prompt: '[1] (citation)\\ntext', separated by blank lines."""
    # TODO Milestone 2
    raise NotImplementedError


def answer_question(
    question: str,
    *,
    store: ChunkStore,
    embedder: Embedder,
    generator: Generator,
    top_k: int,
    min_score: float,
) -> Answer:
    """Answer `question` from the index, citing the sources used.

    The question is stripped of surrounding whitespace first.

    - Nothing retrieved above `min_score`: not found (`NOT_FOUND`, no sources, model
      None), without calling the generator.
    - The generator says the sources don't answer it (answerable is false): not found,
      with no sources, but with the model and token counts it reported.
    - Otherwise the answer, with exactly the cited sources, in number order, each keeping
      the number it had in the context. A source counts as cited if its number is in the
      answer's `citations`, or appears as [n] in the answer's text.

    Raises InvalidAnswerError if an answer cites no sources, or a number that wasn't
    given; GenerationError subclasses from the generator pass through. Logs counts and
    outcomes, never the question or the answer.
    """
    # TODO Milestone 2
    raise NotImplementedError
