"""Finding, fingerprinting and reading the documents to index."""

import hashlib  # noqa: F401  (you'll need it in content_hash)
from pathlib import Path

from pypdf import PdfReader  # noqa: F401  (you'll need these in load_document)
from pypdf.errors import PdfReadError  # noqa: F401

from knowledge_assistant.errors import DocumentError  # noqa: F401
from knowledge_assistant.models import Document

SUPPORTED = (".md", ".pdf")


def discover(folder: Path) -> dict[str, Path]:
    """Every supported file under `folder`, including subfolders, keyed by source, sorted.

    A source is the file's path relative to `folder`, with '/' separators on every
    operating system: 'runbooks/vpn-outage.md'. Suffixes match case-insensitively. Files
    and folders whose names start with '.' are ignored. Raises DocumentError if `folder`
    isn't a folder.
    """
    # TODO Milestone 2
    raise NotImplementedError


def content_hash(path: Path) -> str:
    """The SHA-256 of the file's bytes, as 64 hexadecimal characters."""
    # TODO Milestone 2
    raise NotImplementedError


def load_document(path: Path, source: str) -> list[Document]:
    """The file's text: one Document for Markdown, one per PDF page that has text.

    Markdown is read as UTF-8 (a byte-order mark is ignored); its title is the first
    '# ' heading, or the file's stem. A PDF's title is its metadata title, or the stem;
    pages are numbered from 1, and pages without text are left out.

    Raises DocumentError, with a message that names `source` and never quotes the
    file, when the file isn't UTF-8, isn't a readable PDF, has no text at all, or has
    an unsupported suffix.
    """
    # TODO Milestone 2
    raise NotImplementedError
