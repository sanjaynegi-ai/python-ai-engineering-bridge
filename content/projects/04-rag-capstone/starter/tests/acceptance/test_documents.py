"""Milestone 2: finding, fingerprinting and loading documents. Do not edit."""

import hashlib

import pytest

from knowledge_assistant.documents import content_hash, discover, load_document
from knowledge_assistant.errors import DocumentError

# -- discover ------------------------------------------------------------------------------


def test_discover_finds_every_sample_document_in_subfolders(docs):
    found = discover(docs)
    assert len(found) == 24
    assert "runbooks/vpn-outage.md" in found
    assert "policies/sla-and-priorities.pdf" in found
    assert found["runbooks/vpn-outage.md"] == docs / "runbooks" / "vpn-outage.md"


def test_discover_uses_forward_slashes_and_sorted_order(docs):
    (docs / "zz-top-level.md").write_text("# Top\n\nText.", encoding="utf-8")
    sources = list(discover(docs))
    assert sources[-1] == "zz-top-level.md"
    assert sources == sorted(sources)
    assert all("\\" not in source for source in sources)


def test_discover_ignores_unsupported_and_hidden_files(docs):
    (docs / "notes.txt").write_text("not indexed", encoding="utf-8")
    (docs / ".draft.md").write_text("# Hidden\n\nnot indexed", encoding="utf-8")
    (docs / ".obsidian").mkdir()
    (docs / ".obsidian" / "workspace.md").write_text("# Hidden\n\ntext", encoding="utf-8")
    sources = discover(docs)
    assert "README.txt" not in sources
    assert "notes.txt" not in sources
    assert ".draft.md" not in sources
    assert not any(source.startswith(".obsidian") for source in sources)


def test_discover_matches_suffixes_case_insensitively(docs):
    (docs / "guides" / "SHOUTING.MD").write_text("# Loud\n\nText.", encoding="utf-8")
    assert "guides/SHOUTING.MD" in discover(docs)


def test_discover_rejects_a_missing_folder(tmp_path):
    with pytest.raises(DocumentError):
        discover(tmp_path / "nowhere")


# -- content_hash -------------------------------------------------------------------------


def test_content_hash_is_the_sha256_of_the_bytes(tmp_path):
    path = tmp_path / "a.md"
    path.write_bytes(b"# Title\r\n\r\nWindows line endings.\r\n")
    assert content_hash(path) == hashlib.sha256(path.read_bytes()).hexdigest()


def test_content_hash_changes_with_the_content_but_not_the_name_or_time(tmp_path):
    first, second = tmp_path / "first.md", tmp_path / "second.md"
    first.write_text("# Same\n\nText.", encoding="utf-8")
    second.write_text("# Same\n\nText.", encoding="utf-8")
    assert content_hash(first) == content_hash(second)
    second.write_text("# Same\n\nText!", encoding="utf-8")
    assert content_hash(first) != content_hash(second)


# -- load_document: Markdown --------------------------------------------------------------


def test_markdown_is_one_document_with_its_title_and_source(docs):
    path = docs / "runbooks" / "vpn-outage.md"
    [document] = load_document(path, "runbooks/vpn-outage.md")
    assert document.source == "runbooks/vpn-outage.md"
    assert document.title == "Runbook: Office VPN Problems"
    assert document.page is None
    assert "vpn-ber" in document.text


def test_markdown_title_falls_back_to_the_file_stem(tmp_path):
    path = tmp_path / "no-heading.md"
    path.write_text("Just a paragraph, with no heading at all.", encoding="utf-8")
    [document] = load_document(path, "no-heading.md")
    assert document.title == "no-heading"


def test_a_byte_order_mark_does_not_hide_the_title(tmp_path):
    path = tmp_path / "notepad.md"
    path.write_bytes("﻿# Saved by Notepad\n\nBody text.".encode())
    [document] = load_document(path, "notepad.md")
    assert document.title == "Saved by Notepad"
    assert "﻿" not in document.text


@pytest.mark.parametrize("content", [b"", b"   \n\n\t\n"])
def test_an_empty_markdown_file_is_a_document_error(tmp_path, content):
    path = tmp_path / "empty.md"
    path.write_bytes(content)
    with pytest.raises(DocumentError, match="empty.md"):
        load_document(path, "guides/empty.md")


def test_markdown_that_is_not_utf8_is_a_document_error(tmp_path):
    path = tmp_path / "latin1.md"
    path.write_bytes("# Café menu\n\nCrème brûlée".encode("latin-1"))
    with pytest.raises(DocumentError, match="latin1.md"):
        load_document(path, "guides/latin1.md")


# -- load_document: PDF -------------------------------------------------------------------


def test_a_pdf_gives_one_document_per_page_with_page_numbers(docs):
    path = docs / "policies" / "on-call-rota.pdf"
    documents = load_document(path, "policies/on-call-rota.pdf")
    assert [document.page for document in documents] == [1, 2]
    assert all(document.title == "Policy: On-Call Rota" for document in documents)
    assert all(document.source == "policies/on-call-rota.pdf" for document in documents)
    assert "Swaps" in documents[1].text


def test_a_pdf_with_no_text_is_a_document_error(blank_pdf):
    with pytest.raises(DocumentError, match="scanned.pdf"):
        load_document(blank_pdf, "scanned.pdf")


@pytest.mark.parametrize(
    "content",
    [b"", b"%PDF-1.7\n", b"this is not a PDF at all\n" * 5],
    ids=["empty", "header-only", "not-a-pdf"],
)
def test_a_corrupt_pdf_is_a_document_error(tmp_path, content):
    path = tmp_path / "broken.pdf"
    path.write_bytes(content)
    with pytest.raises(DocumentError, match="broken.pdf"):
        load_document(path, "policies/broken.pdf")


def test_a_truncated_pdf_is_a_document_error(docs, tmp_path):
    original = (docs / "policies" / "on-call-rota.pdf").read_bytes()
    path = tmp_path / "half.pdf"
    path.write_bytes(original[: len(original) // 2])
    with pytest.raises(DocumentError, match="half.pdf"):
        load_document(path, "policies/half.pdf")


def test_errors_name_the_source_but_never_quote_the_file(tmp_path):
    secret = "CANARY-7f3a the contents of this file must not appear in errors"
    path = tmp_path / "leaky.md"
    path.write_bytes(f"# {secret}\n\n{secret}, café".encode("latin-1"))  # not UTF-8
    with pytest.raises(DocumentError) as caught:
        load_document(path, "guides/leaky.md")
    assert "guides/leaky.md" in str(caught.value)
    assert "CANARY" not in str(caught.value)
