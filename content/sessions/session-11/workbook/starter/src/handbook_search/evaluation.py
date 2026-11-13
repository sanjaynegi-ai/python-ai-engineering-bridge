"""Measuring retrieval with a set of questions whose answers are known."""

import json
from dataclasses import dataclass, field
from pathlib import Path

from handbook_search.embedding import Embedder
from handbook_search.retrieval import retrieve  # noqa: F401  (you will need it)
from handbook_search.store import VectorStore


@dataclass(frozen=True)
class EvaluationQuestion:
    question: str
    expected_sources: frozenset[str]  # empty: the handbook doesn't answer it


@dataclass
class EvaluationResult:
    answerable: int = 0
    hits: int = 0  # answerable questions with an expected source among the results
    unanswerable: int = 0
    correctly_empty: int = 0  # unanswerable questions with no results at all
    misses: list[str] = field(default_factory=list)  # questions that went wrong, either way

    @property
    def hit_rate(self) -> float:
        return self.hits / self.answerable if self.answerable else 0.0

    @property
    def rejection_rate(self) -> float:
        return self.correctly_empty / self.unanswerable if self.unanswerable else 0.0


def load_questions(path: Path) -> list[EvaluationQuestion]:
    """JSON Lines: {"question": "...", "expected_sources": ["file.md", ...]} per line."""
    questions = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            data = json.loads(line)
            questions.append(
                EvaluationQuestion(data["question"], frozenset(data["expected_sources"]))
            )
    return questions


def evaluate(
    store: VectorStore,
    embedder: Embedder,
    questions: list[EvaluationQuestion],
    *,
    k: int,
    min_score: float,
) -> EvaluationResult:
    """Retrieve for every question and count the results.

    An answerable question is a hit when any expected source is among the retrieved chunks'
    sources. An unanswerable question (no expected sources) is correctly empty when
    nothing is retrieved. Every other question goes into `misses`.
    """
    # TODO Milestone 6
    raise NotImplementedError
