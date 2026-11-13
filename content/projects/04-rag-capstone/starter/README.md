# knowledge-assistant

The Internal Knowledge Assistant for Orbital Logistics IT operations: ask a question about the runbooks, policies, postmortems and guides, and get an answer grounded in them, with sources. Orbital Logistics is a fictional company, and every document in `data/docs/` is synthetic.

This is **Project 04**, the course capstone. It grows over three sessions:

| Session | What's added |
|---|---|
| 14 | Ingestion: find, fingerprint, load, chunk, embed and store the documents, doing only the work that changed (**this stage**) |
| 15 | Answers: retrieval, a grounded prompt, the LLM's answer with sources, a FastAPI service, a Streamlit UI, and an evaluation |
| 16 | Review: integration tests, logging, and a presentation of the design |

## What you build in this stage

Follow the Session 14 workbook (`sessions/session-14/workbook/assignment.md` in the course repository). You write the four modules marked **you** below; everything else, including the command line, is provided. The acceptance tests in `tests/acceptance/` define what "done" means, one file per milestone. Until you've written the modules, the commands below fail with `NotImplementedError`.

## Setup

```bash
uv sync
```

No API key is needed for this stage. The default embedder, fastembed, runs `BAAI/bge-small-en-v1.5` on your machine; the first run downloads it (about 67 MB) unless Session 11 already did. Set `ASSISTANT_EMBEDDER=hashing` for an instant, download-free embedder that matches words rather than meaning. The tests always use it.

## Usage

```bash
uv run knowledge-assistant ingest              # index data/docs: only new and changed files
uv run knowledge-assistant ingest --rebuild    # start again from an empty index
uv run knowledge-assistant status              # what the index holds
uv run knowledge-assistant search "How do I promote the orders database replica?"
uv run knowledge-assistant -v ingest           # log every file
```

| Exit code | Meaning |
|---:|---|
| `0` | Success |
| `1` | `ingest`: some files failed, and are listed on stderr; `status`: the index is empty; `search`: nothing found |
| `2` | No run: invalid settings, a missing documents folder, or an index built with different settings (rebuild it) |

Settings come from `ASSISTANT_*` environment variables or `.env`: see `.env.example`.

## Project layout

```text
knowledge-assistant/
├── .env.example            documented settings; copy to .env
├── data/docs/              the documents to index (synthetic), in four folders
├── src/knowledge_assistant/
│   ├── models.py           Document, Chunk, Hit, IndexConfig, IngestReport
│   ├── settings.py         Settings (pydantic-settings)
│   ├── errors.py           DocumentError, IndexMismatchError
│   ├── embedding.py        the Embedder protocol, HashingEmbedder, FastEmbedEmbedder
│   ├── documents.py        you: discover, content_hash, load_document
│   ├── chunking.py         you: chunk_document
│   ├── store.py            you: ChunkStore, the index in a local Chroma database
│   ├── ingestion.py        you: ingest, which brings the index up to date
│   └── cli.py              the knowledge-assistant command
└── tests/
    ├── conftest.py         shared fixtures
    ├── acceptance/         provided tests; do not edit
    └── unit/               your own tests
```

## Development

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```
