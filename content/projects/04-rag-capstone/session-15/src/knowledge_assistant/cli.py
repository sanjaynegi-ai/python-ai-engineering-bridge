"""Command line: `knowledge-assistant ingest | status | search | ask | evaluate`.

Exit codes:
    0  success
    1  ingest: some files failed; status: the index is empty; search: nothing found;
       ask: not found in the documentation; evaluate: some questions failed with an error
    2  invalid settings, a missing documents folder, an index built with other settings,
       or the language model failed or is misconfigured
"""

import argparse
import logging
import sys
from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import SettingsError

from knowledge_assistant.assistant import build_assistant, open_store
from knowledge_assistant.embedding import Embedder, make_embedder
from knowledge_assistant.errors import AssistantError, IndexMismatchError
from knowledge_assistant.evaluation import evaluate, load_questions
from knowledge_assistant.ingestion import ingest
from knowledge_assistant.settings import Settings


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


def run_ask(settings: Settings, question: str) -> int:
    answer = build_assistant(settings).ask(question)
    print(answer.answer)
    if not answer.found:
        return 1
    print()
    for source in answer.sources:
        print(f"[{source.number}] {source.citation}  (score {source.score:.3f})")
    if answer.model:
        print(
            f"\n{answer.model}: {answer.input_tokens} input, {answer.output_tokens} output tokens"
        )
    return 0


def run_evaluate(settings: Settings, path: Path) -> int:
    assistant = build_assistant(settings)
    report = evaluate(assistant, load_questions(path))
    answerable, unanswerable = len(report.answerable), len(report.unanswerable)
    print(f"{len(report.results)} questions: {answerable} answerable, {unanswerable} unanswerable")
    print(
        f"generator {assistant.generator.model_id}, "
        f"top {assistant.top_k}, min score {assistant.min_score}"
    )
    print(f"retrieval hit rate  {report.retrieval_hit_rate:6.0%}  expected source retrieved")
    print(f"answer rate         {report.answer_rate:6.0%}  answerable questions answered")
    print(f"grounded rate       {report.grounded_rate:6.0%}  answers citing an expected source")
    print(f"rejection rate      {report.rejection_rate:6.0%}  unanswerable questions declined")
    for result in report.results:
        item = result.item
        if result.error:
            problem = f"error: {result.error}"
        elif item.answerable and not result.retrieval_hit:
            problem = f"not retrieved; got {result.retrieved[:3] or 'nothing'}"
        elif item.answerable and not result.grounded:
            problem = f"not grounded; cited {result.cited or 'nothing'}"
        elif not item.answerable and not result.correctly_rejected:
            problem = f"answered anyway, citing {result.cited}"
        else:
            continue
        print(f"  {item.question}\n      {problem}")
    return 1 if report.errors else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="knowledge-assistant")
    parser.add_argument("-v", "--verbose", action="store_true", help="log every step")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("ingest", help="bring the index up to date with the documents")
    build.add_argument(
        "--rebuild", action="store_true", help="delete the index and build it from scratch"
    )
    commands.add_parser("status", help="list what the index holds")
    find = commands.add_parser("search", help="show the chunks closest to a question")
    find.add_argument("question")
    find.add_argument("-k", type=int, default=3, help="how many chunks (default 3)")
    ask = commands.add_parser("ask", help="answer a question from the documentation")
    ask.add_argument("question")
    check = commands.add_parser("evaluate", help="measure the assistant on known questions")
    check.add_argument("questions", type=Path, nargs="?", default=Path("data/eval/questions.jsonl"))
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    # pypdf logs the first bytes of a file it can't parse; the ingest report covers it.
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    # HTTP clients log every request at INFO; the assistant logs what matters.
    logging.getLogger("httpx2").setLevel(logging.WARNING)

    try:
        settings = Settings()
    except (SettingsError, ValidationError) as error:
        print(f"error: invalid settings: {error}", file=sys.stderr)
        return 2

    try:
        if args.command == "ask":
            return run_ask(settings, args.question)
        if args.command == "evaluate":
            return run_evaluate(settings, args.questions)
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
    except (ValueError, FileNotFoundError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
