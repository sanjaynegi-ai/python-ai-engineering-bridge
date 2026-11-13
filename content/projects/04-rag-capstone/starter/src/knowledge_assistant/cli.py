"""Command line: `knowledge-assistant ingest [--rebuild] | status | search QUESTION`.

Exit codes:
    0  success
    1  ingest: some files failed; status: the index is empty; search: nothing found
    2  invalid settings, a missing documents folder, or an index built with other settings
"""

import argparse
import logging
import sys

from pydantic import ValidationError
from pydantic_settings import SettingsError

from knowledge_assistant.embedding import Embedder, make_embedder
from knowledge_assistant.errors import AssistantError, IndexMismatchError
from knowledge_assistant.ingestion import ingest
from knowledge_assistant.models import IndexConfig
from knowledge_assistant.settings import Settings
from knowledge_assistant.store import ChunkStore


def open_store(settings: Settings, embedder: Embedder, *, rebuild: bool = False) -> ChunkStore:
    config = IndexConfig(
        embedding_model=embedder.model_id,
        dimensions=embedder.dimensions,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return ChunkStore(settings.index, config, rebuild=rebuild)


def run_ingest(settings: Settings, embedder: Embedder, *, rebuild: bool) -> int:
    store = open_store(settings, embedder, rebuild=rebuild)
    report = ingest(settings.documents, store, embedder)
    for reason in report.failed.values():
        print(f"failed {reason}", file=sys.stderr)
    print(
        f"{len(report.added)} added, {len(report.updated)} updated, "
        f"{len(report.unchanged)} unchanged, {len(report.removed)} removed, "
        f"{len(report.failed)} failed"
    )
    print(
        f"Index: {store.count()} chunks from {len(store.sources())} files in {settings.index} "
        f"({embedder.model_id})"
    )
    return 0 if report.ok else 1


def run_status(settings: Settings, embedder: Embedder) -> int:
    store = open_store(settings, embedder)
    sources = store.sources()
    if not sources:
        print("The index is empty: run 'knowledge-assistant ingest'.")
        return 1
    for source, digest in sources.items():
        print(f"{source:<50} {len(store.chunks(source)):>3} chunks  sha256:{digest[:12]}")
    config = store.config
    print(
        f"{store.count()} chunks from {len(sources)} files; model {config.embedding_model}, "
        f"chunk size {config.chunk_size}, overlap {config.chunk_overlap}"
    )
    return 0


def run_search(settings: Settings, embedder: Embedder, question: str, k: int) -> int:
    store = open_store(settings, embedder)
    hits = store.search(embedder.embed([question])[0], k=k)
    if not hits:
        print("Nothing found: is the index empty?")
        return 1
    for number, hit in enumerate(hits, 1):
        preview = " ".join(hit.chunk.text.split())[:70]
        print(f"[{number}] {hit.score:.3f}  {hit.chunk.citation}\n    {preview}...")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="knowledge-assistant")
    parser.add_argument("-v", "--verbose", action="store_true", help="log every file")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("ingest", help="bring the index up to date with the documents")
    build.add_argument(
        "--rebuild", action="store_true", help="delete the index and build it from scratch"
    )
    commands.add_parser("status", help="list what the index holds")
    find = commands.add_parser("search", help="show the chunks closest to a question")
    find.add_argument("question")
    find.add_argument("-k", type=int, default=3, help="how many chunks (default 3)")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    # pypdf logs the first bytes of a file it can't parse; the ingest report covers it.
    logging.getLogger("pypdf").setLevel(logging.ERROR)

    try:
        settings = Settings()
    except (SettingsError, ValidationError) as error:
        print(f"error: invalid settings: {error}", file=sys.stderr)
        return 2

    try:
        embedder = make_embedder(settings)
        if args.command == "ingest":
            return run_ingest(settings, embedder, rebuild=args.rebuild)
        if args.command == "status":
            return run_status(settings, embedder)
        return run_search(settings, embedder, args.question, args.k)
    except IndexMismatchError as error:
        print(f"error: {error}", file=sys.stderr)
        print("Run 'knowledge-assistant ingest --rebuild' to rebuild the index.", file=sys.stderr)
        return 2
    except AssistantError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
