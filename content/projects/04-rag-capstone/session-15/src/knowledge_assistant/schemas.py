"""The assistant's public contract: what a question looks like, and what an answer contains.

FastAPI validates requests and documents responses with these models; the UI and the
CLI display them.
"""

from pydantic import BaseModel, Field, field_validator


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)

    @field_validator("question")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("the question is blank")
        return value.strip()


class SourceRef(BaseModel):
    """One source an answer cites. `number` is the [n] used in the answer's text."""

    number: int
    source: str
    title: str
    section: str | None = None
    page: int | None = None
    score: float
    citation: str  # for people: 'policies/sla-and-priorities.pdf, page 1'


class Answer(BaseModel):
    question: str
    answer: str
    found: bool  # False: the documentation doesn't answer it, and `answer` says so
    sources: list[SourceRef] = Field(default_factory=list)  # only the cited ones
    model: str | None = None  # None when no model was called
    input_tokens: int = 0
    output_tokens: int = 0
