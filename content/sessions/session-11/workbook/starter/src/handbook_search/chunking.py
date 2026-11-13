"""Splitting documents into chunks that keep their metadata."""

from handbook_search.models import Chunk, Document


def split_sections(markdown: str) -> list[tuple[str | None, str]]:
    """(section heading, body) pairs, split at '## ' headings.

    Text before the first '## ' heading belongs to section None. '# ' title lines are
    dropped. Bodies are stripped, and sections with an empty body are left out.
    """
    # TODO Milestone 3
    raise NotImplementedError


def split_text(text: str, size: int, overlap: int) -> list[str]:
    """Pieces of at most `size` characters, with whitespace normalised.

    Text is split into units at line breaks and after sentence-ending punctuation; units
    are joined with single spaces up to `size`. Each new piece starts with as many of the
    previous piece's final units as fit in `overlap` characters. A single unit longer than
    `size` becomes a piece of its own.
    """
    # TODO Milestone 3
    raise NotImplementedError


def chunk_documents(documents: list[Document], *, size: int, overlap: int) -> list[Chunk]:
    """Chunks for every document, in order, with source, title, section, page and index.

    Markdown documents (page None) are split into sections first; PDF pages are chunked
    as a whole, with section None. The index counts chunks per source file, from 0,
    across all pages of a PDF.
    """
    # TODO Milestone 3
    raise NotImplementedError
