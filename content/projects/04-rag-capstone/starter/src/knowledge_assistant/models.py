"""The data that flows through the assistant: documents, chunks, search hits and reports."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Document:
    """The text of one Markdown file, or of one PDF page."""

    source: str  # the file's path inside the documents folder, with '/' separators
    title: str
    text: str
    page: int | None = None  # PDF page number, from 1; None for Markdown


@dataclass(frozen=True)
class Chunk:
    """A passage of a document, with everything needed to cite it and to keep it current."""

    text: str
    source: str
    title: str
    section: str | None  # the '## ' heading it sits under; None before the first, and for PDFs
    page: int | None
    index: int  # position of the chunk within its source file, from 0
    content_hash: str  # SHA-256 of the source file's bytes, when the chunk was made

    @property
    def id(self) -> str:
        """A stable ID: the same file and position always give the same ID."""
        return f"{self.source}#{self.index}"

    @property
    def embedding_text(self) -> str:
        """What gets embedded: the text, with its title and section for context."""
        heading = " / ".join(part for part in (self.title, self.section) if part)
        return f"{heading}\n{self.text}"

    @property
    def citation(self) -> str:
        """Where the chunk came from, for people: 'a/file.pdf, page 2' or 'a/file.md, Section'."""
        where = self.source
        if self.page is not None:
            where += f", page {self.page}"
        if self.section:
            where += f", {self.section}"
        return where


@dataclass(frozen=True)
class Hit:
    """One search result: a chunk and its cosine similarity to the query."""

    score: float
    chunk: Chunk


@dataclass(frozen=True)
class IndexConfig:
    """Everything that decides what's in an index, apart from the documents themselves.

    An index built with one configuration can't be updated with another: the vectors or
    the chunk boundaries wouldn't match.
    """

    embedding_model: str
    dimensions: int
    chunk_size: int
    chunk_overlap: int


@dataclass
class IngestReport:
    """What one ingestion run did, by source. Reasons never contain document text."""

    added: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)  # source -> reason
    chunks_written: int = 0

    @property
    def ok(self) -> bool:
        return not self.failed
