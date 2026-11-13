"""Measuring the assistant on questions whose answers are known."""

import json  # noqa: F401  (you'll need it in load_questions)
from dataclasses import dataclass, field
from pathlib import Path

from knowledge_assistant.answering import retrieve  # noqa: F401
from knowledge_assistant.assistant import Assistant
from knowledge_assistant.errors import GenerationError  # noqa: F401


@dataclass(frozen=True)
class EvalQuestion:
    question: str
    expected_sources: frozenset[str]  # empty: the documentation doesn't answer it

    @property
    def answerable(self) -> bool:
        return bool(self.expected_sources)


@dataclass
class QuestionResult:
    item: EvalQuestion
    retrieved: list[str] = field(default_factory=list)  # sources above the threshold, best first
    found: bool = False
    cited: list[str] = field(default_factory=list)  # sources the answer cites
    error: str | None = None  # a GenerationError's message, if generation failed

    @property
    def retrieval_hit(self) -> bool:
        """Answerable, and an expected source was among the retrieved chunks."""
        # TODO Milestone 5
        raise NotImplementedError

    @property
    def grounded(self) -> bool:
        """Answerable, answered, and the answer cites an expected source."""
        # TODO Milestone 5
        raise NotImplementedError

    @property
    def correctly_rejected(self) -> bool:
        """Unanswerable, and the assistant said it can't find it (without an error)."""
        # TODO Milestone 5
        raise NotImplementedError


@dataclass
class EvaluationReport:
    results: list[QuestionResult]

    @property
    def answerable(self) -> list[QuestionResult]:
        return [r for r in self.results if r.item.answerable]

    @property
    def unanswerable(self) -> list[QuestionResult]:
        return [r for r in self.results if not r.item.answerable]

    # Each rate is a fraction of its group (answerable or unanswerable questions), from
    # 0.0 to 1.0; an empty group gives 0.0.

    @property
    def retrieval_hit_rate(self) -> float:
        # TODO Milestone 5
        raise NotImplementedError

    @property
    def answer_rate(self) -> float:
        """Answerable questions that got an answer (found, no error)."""
        # TODO Milestone 5
        raise NotImplementedError

    @property
    def grounded_rate(self) -> float:
        # TODO Milestone 5
        raise NotImplementedError

    @property
    def rejection_rate(self) -> float:
        # TODO Milestone 5
        raise NotImplementedError

    @property
    def errors(self) -> int:
        return sum(1 for r in self.results if r.error is not None)


def load_questions(path: Path) -> list[EvalQuestion]:
    """JSON Lines: {"question": "...", "expected_sources": ["runbooks/x.md", ...]} per line.

    Blank lines are skipped.
    """
    # TODO Milestone 5
    raise NotImplementedError


def evaluate(assistant: Assistant, questions: list[EvalQuestion]) -> EvaluationReport:
    """Retrieve and answer every question, recording what happened to each.

    `retrieved` comes from retrieve() with the assistant's top_k and min_score; `found`
    and `cited` from assistant.ask(). A GenerationError for one question is recorded in
    its result, and the evaluation carries on with the next.
    """
    # TODO Milestone 5
    raise NotImplementedError
