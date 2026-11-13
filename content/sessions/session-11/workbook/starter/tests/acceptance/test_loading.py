"""Acceptance tests for loading PDFs and folders (workbook Milestone 2). Do not edit."""

import pytest

from handbook_search.errors import DocumentError
from handbook_search.loading import load_documents, load_pdf
from handbook_search.models import Document


def test_pdf_gives_one_document_per_page(handbook):
    pages = load_pdf(handbook / "policy-incident-communication.pdf")

    assert [page.page for page in pages] == [1, 2]
    assert all(isinstance(page, Document) for page in pages)
    assert {page.source for page in pages} == {"policy-incident-communication.pdf"}


def test_pdf_title_comes_from_its_metadata(handbook):
    pages = load_pdf(handbook / "sla-and-priorities.pdf")

    assert pages[0].title == "Policy: Service Levels and Priorities"


def test_pdf_text_is_extracted(handbook):
    text = load_pdf(handbook / "sla-and-priorities.pdf")[0].text

    assert "P2, 24 hours" in text


def test_pdf_page_without_text_is_skipped(blank_pdf):
    assert load_pdf(blank_pdf) == []


def test_pdf_title_falls_back_to_the_file_name(handbook, tmp_path):
    from pypdf import PdfReader, PdfWriter

    writer = PdfWriter(clone_from=PdfReader(handbook / "sla-and-priorities.pdf"))
    writer.metadata = None  # no title in the metadata
    path = tmp_path / "untitled.pdf"
    with open(path, "wb") as file:
        writer.write(file)

    pages = load_pdf(path)

    assert [page.title for page in pages] == ["untitled"]


def test_damaged_pdf_raises_document_error(tmp_path):
    path = tmp_path / "damaged.pdf"
    path.write_bytes(b"%PDF-1.7\nthis is not really a PDF")

    with pytest.raises(DocumentError) as caught:
        load_pdf(path)

    assert "damaged.pdf" in str(caught.value)


def test_folder_loads_markdown_and_pdf_in_name_order(handbook):
    documents, problems = load_documents(handbook)

    assert problems == []
    assert len(documents) == 13  # 10 Markdown files, and 3 PDF pages
    assert [d.source for d in documents] == sorted(d.source for d in documents)
    assert documents[0].source == "guide-phishing-response.md"


def test_folder_ignores_other_files(handbook):
    documents, _ = load_documents(handbook)

    assert "README.txt" not in {d.source for d in documents}


def test_folder_reports_problem_files_and_keeps_going(handbook, blank_pdf):
    (handbook / "broken.md").write_bytes(b"\xff\xfe not utf-8")
    (handbook / "damaged.pdf").write_bytes(b"not a pdf")
    blank_pdf.rename(handbook / "scanned.pdf")

    documents, problems = load_documents(handbook)

    assert len(documents) == 13
    assert len(problems) == 3
    assert any("broken.md" in p for p in problems)
    assert any("damaged.pdf" in p for p in problems)
    assert any("scanned.pdf" in p and "no text" in p for p in problems)


def test_missing_folder_raises_document_error(tmp_path):
    with pytest.raises(DocumentError):
        load_documents(tmp_path / "nowhere")
