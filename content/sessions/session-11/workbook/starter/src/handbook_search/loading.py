"""Loading Markdown and PDF files into Documents."""

from pathlib import Path

from pypdf import PdfReader  # noqa: F401  (you'll need it in load_pdf)
from pypdf.errors import PdfReadError  # noqa: F401

from handbook_search.errors import DocumentError  # noqa: F401
from handbook_search.models import Document

SUPPORTED = {".md", ".pdf"}


def load_markdown(path: Path) -> list[Document]:
    """One Document for the whole file; the title is the first '# ' heading, or the file stem."""
    text = path.read_text(encoding="utf-8")
    first_line = text.splitlines()[0] if text else ""
    title = first_line[2:].strip() if first_line.startswith("# ") else path.stem
    return [Document(source=path.name, title=title, text=text)]


def load_pdf(path: Path) -> list[Document]:
    """One Document per page that has text, numbered from 1.

    The title is the PDF's metadata title, or the file stem. Pages without text (for
    example scanned images) are skipped. A file that isn't a readable PDF raises
    DocumentError, with the file name in the message.
    """
    # TODO Milestone 2
    raise NotImplementedError


def load_documents(folder: Path) -> tuple[list[Document], list[str]]:
    """Every supported file in `folder`, in name order, and a list of problems.

    A file that can't be loaded, or that yields no text, is reported as a problem and
    skipped; it never stops the other files from loading. A missing folder raises
    DocumentError.
    """
    # TODO Milestone 2
    raise NotImplementedError
