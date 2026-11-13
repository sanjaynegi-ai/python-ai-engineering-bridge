"""The data that flows through ingestion and retrieval."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    """The text of one Markdown file, or of one PDF page."""

    source: str  # the file name: what answers cite
    title: str
    text: str
    page: int | None = None  # PDF page number, from 1; None for Markdown


@dataclass(frozen=True)
class Chunk:
    """A passage of a document, with everything needed to cite it."""

    text: str
    source: str
    title: str
    section: str | None
    page: int | None
    index: int  # position of the chunk within its source file, from 0

    @property
    def embedding_text(self) -> str:
        """What gets embedded: the text, with its title and section for context."""
        heading = " / ".join(part for part in (self.title, self.section) if part)
        return f"{heading}\n{self.text}"

    @property
    def citation(self) -> str:
        """Where the chunk came from, for people: 'file.pdf, page 2' or 'file.md, Section'."""
        where = self.source
        if self.page is not None:
            where += f", page {self.page}"
        if self.section:
            where += f", {self.section}"
        return where


@dataclass(frozen=True)
class Hit:
    """One search result."""

    score: float
    chunk: Chunk
