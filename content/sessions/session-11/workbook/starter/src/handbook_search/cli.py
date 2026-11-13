"""Command line: `handbook-search ingest | query QUESTION | evaluate QUESTIONS.jsonl`.

Exit codes:
    0  success
    1  ingest: some files were skipped; query: nothing relevant found;
       evaluate: some questions went wrong
    2  invalid settings, a missing folder, or no usable index
"""

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import SettingsError

from handbook_search.chunking import chunk_documents
from handbook_search.embedding import Embedder, FastEmbedEmbedder, HashingEmbedder
from handbook_search.errors import DocumentError, SearchIndexError
from handbook_search.evaluation import evaluate, load_questions
from handbook_search.loading import load_documents
from handbook_search.retrieval import NOT_FOUND, build_context, retrieve
from handbook_search.settings import Settings
from handbook_search.store import VectorStore


def make_embedder(settings: Settings) -> Embedder:
    if settings.embedder == "hashing":
        return HashingEmbedder()
    return FastEmbedEmbedder(settings.embedding_model)


def ingest(settings: Settings, embedder: Embedder) -> int:
    documents, problems = load_documents(settings.documents)
    chunks = chunk_documents(documents, size=settings.chunk_size, overlap=settings.chunk_overlap)
    store = VectorStore(embedder.model_id, embedder.dimensions)
    store.add(chunks, embedder.embed([chunk.embedding_text for chunk in chunks]))
    store.save(settings.index)
    for problem in problems:
        print(f"skipped {problem}", file=sys.stderr)
    files = len({document.source for document in documents})
    print(f"Indexed {len(chunks)} chunks from {files} files into {settings.index}")
    print(f"Embedding model: {embedder.model_id}")
    return 1 if problems else 0


def query(settings: Settings, embedder: Embedder, question: str) -> int:
    store = VectorStore.load(settings.index, model_id=embedder.model_id)
    hits = retrieve(store, embedder, question, k=settings.top_k, min_score=settings.min_score)
    if not hits:
        print(NOT_FOUND)
        return 1
    for number, hit in enumerate(hits, 1):
        print(f"[{number}] {hit.score:.3f}  {hit.chunk.citation}")
    print()
    print(build_context(hits))
    return 0


def run_evaluation(settings: Settings, embedder: Embedder, path: Path) -> int:
    store = VectorStore.load(settings.index, model_id=embedder.model_id)
    result = evaluate(
        store, embedder, load_questions(path), k=settings.top_k, min_score=settings.min_score
    )
    print(
        f"hit rate {result.hit_rate:.0%} ({result.hits}/{result.answerable} answerable questions)"
    )
    print(
        f"rejected {result.rejection_rate:.0%} "
        f"({result.correctly_empty}/{result.unanswerable} unanswerable questions)"
    )
    for miss in result.misses:
        print(f"  wrong: {miss}")
    return 1 if result.misses else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="handbook-search")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("ingest", help="index the documents folder")
    ask = commands.add_parser("query", help="find the passages that answer a question")
    ask.add_argument("question")
    check = commands.add_parser("evaluate", help="measure retrieval on known questions")
    check.add_argument("questions", type=Path)
    args = parser.parse_args(argv)

    try:
        settings = Settings()
    except (SettingsError, ValidationError) as error:
        print(f"error: invalid settings: {error}", file=sys.stderr)
        return 2

    try:
        embedder = make_embedder(settings)
        if args.command == "ingest":
            return ingest(settings, embedder)
        if args.command == "query":
            return query(settings, embedder, args.question)
        return run_evaluation(settings, embedder, args.questions)
    except (DocumentError, SearchIndexError, ValueError, FileNotFoundError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
