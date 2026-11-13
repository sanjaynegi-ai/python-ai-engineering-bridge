"""Splitting one file's documents into chunks that keep their metadata."""

from knowledge_assistant.models import Chunk, Document


def chunk_document(
    documents: list[Document], content_hash: str, *, size: int, overlap: int
) -> list[Chunk]:
    """Chunks for one file's documents, in order, each at most `size` characters.

    Markdown (page None) is split into sections at '## ' headings first, and each chunk
    records its section: None for text before the first '## ' heading. The '# ' title
    line and the '## ' heading lines are metadata, not chunk text. A PDF page is chunked
    as a whole, with section None, and no chunk spans two pages. Consecutive chunks of
    the same section share up to `overlap` characters. The index counts the file's
    chunks from 0; every chunk carries `content_hash`. No chunk is empty or blank.
    """
    # TODO Milestone 3
    raise NotImplementedError
