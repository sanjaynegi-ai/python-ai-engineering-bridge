# handbook-search

Search the IT handbook of the fictional Orbital Logistics by meaning, and get back the passages that answer a question, with their sources. This is the retrieval half of a RAG application: everything up to, but not including, the LLM call. All documents are synthetic.

## Setup

```bash
uv sync
```

The default embedder is a real embedding model, `BAAI/bge-small-en-v1.5`, run locally with fastembed. The first `ingest` downloads it (about 67 MB) into `~/.cache/fastembed`, or into `FASTEMBED_CACHE_PATH` if you set it in Session 01; after that, it works offline. Nothing is sent to a paid API.

## Usage

```bash
uv run handbook-search ingest
uv run handbook-search query "The Berlin office VPN keeps disconnecting."
uv run handbook-search evaluate data/questions.jsonl
```

`ingest` reads every `.md` and `.pdf` file in the documents folder, chunks it, embeds the chunks, and saves the index. Run it again after you change the documents, the chunk settings, or the embedding model.

| Exit code | Meaning |
|---:|---|
| `0` | Success |
| `1` | `ingest`: some files were skipped. `query`: nothing relevant found. `evaluate`: some questions went wrong |
| `2` | Invalid settings, a missing documents folder, or no usable index |

## Settings

Read from `HANDBOOK_*` environment variables or a `.env` file in the working folder. There are no secrets here, so there's no `.env.example`: every setting has a working default.

| Variable | Default | Meaning |
|---|---|---|
| `HANDBOOK_DOCUMENTS` | `data/handbook` | Folder of documents to index |
| `HANDBOOK_INDEX` | `index` | Where the index is saved (git-ignored) |
| `HANDBOOK_EMBEDDER` | `fastembed` | `fastembed` (a real model) or `hashing` (word matching, for tests) |
| `HANDBOOK_EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | The fastembed model |
| `HANDBOOK_CHUNK_SIZE` | `500` | Maximum characters per chunk |
| `HANDBOOK_CHUNK_OVERLAP` | `100` | Characters repeated between neighbouring chunks; must be smaller than the size |
| `HANDBOOK_TOP_K` | `3` | How many chunks a query returns, at most |
| `HANDBOOK_MIN_SCORE` | `0.6` | Lowest cosine similarity that counts as relevant |

`HANDBOOK_MIN_SCORE` depends on the embedding model: 0.6 suits the default model, but the hashing embedder's scores are much lower.

## Evaluation questions

`data/questions.jsonl` has one question per line, with the files that answer it:

```json
{"question": "How often must we rotate API keys?", "expected_sources": ["policy-api-credentials.md"]}
{"question": "What's on the cafeteria menu this week?", "expected_sources": []}
```

An empty `expected_sources` means the handbook doesn't answer the question, so the right result is nothing at all.

## Project layout

```text
handbook-search/
├── data/
│   ├── handbook/            the documents: 10 Markdown files, 2 PDFs
│   └── questions.jsonl      evaluation questions
├── src/handbook_search/
│   ├── models.py            Document, Chunk, Hit
│   ├── embedding.py         the Embedder protocol, HashingEmbedder, FastEmbedEmbedder
│   ├── settings.py          HANDBOOK_* settings
│   ├── errors.py            DocumentError, SearchIndexError
│   ├── loading.py           Markdown and PDF files to Documents
│   ├── chunking.py          Documents to Chunks
│   ├── store.py             VectorStore: add, search, save, load
│   ├── retrieval.py         retrieve, build_context, cited_numbers
│   ├── evaluation.py        hit rate and rejection rate
│   └── cli.py               the handbook-search command
└── tests/
    ├── conftest.py
    └── acceptance/          the tests that define "done"
```

## Tests

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

The tests use the `HashingEmbedder`, so they're fast, free, and need no model download.

---

<!-- skillup-branding:start -->
## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center">
  <img src="../../../../assets/diagrams/SkillUpWithSanjay.png" alt="#SkillUpWithSanjay logo" width="60">
</p>

<p align="center">
  <strong>#SkillUpWithSanjay</strong><br>
  <a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>
  &nbsp;&middot;&nbsp;
  <a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
</p>
<!-- skillup-branding:end -->
