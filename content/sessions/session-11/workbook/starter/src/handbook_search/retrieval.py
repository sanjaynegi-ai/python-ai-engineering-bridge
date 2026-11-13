"""From a question to retrieved chunks, a prompt context, and checked citations."""

from handbook_search.embedding import Embedder
from handbook_search.models import Hit
from handbook_search.store import VectorStore

NOT_FOUND = "I can't find this in the handbook."


def retrieve(
    store: VectorStore, embedder: Embedder, question: str, *, k: int, min_score: float
) -> list[Hit]:
    """The best chunks for `question`; an empty list means the handbook doesn't cover it.

    Raises ValueError for an empty or blank question.
    """
    # TODO Milestone 5
    raise NotImplementedError


def build_context(hits: list[Hit]) -> str:
    """Numbered sources for a prompt: '[1] (citation)\\ntext', separated by blank lines."""
    # TODO Milestone 5
    raise NotImplementedError


def cited_numbers(answer: str, hits: list[Hit]) -> list[int]:
    """The source numbers cited in `answer` as [n], sorted and without duplicates.

    Raises ValueError if the answer cites a number that wasn't among the sources.
    """
    # TODO Milestone 5
    raise NotImplementedError
