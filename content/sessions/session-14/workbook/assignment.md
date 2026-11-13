# Session 14 Assignment: Capstone Ingestion

**Type:** Milestone 1 is **Independent**: design before you build, without an assistant. Milestones 2 to 6 are **AI-assisted**: you may use Claude Code, or an approved assistant, following the Session 13 workflow. Writing them yourself is just as valid.
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb), and Session 11's `handbook-search`
**Project:** **Project 04**, the capstone: the Internal Knowledge Assistant (`knowledge-assistant`). This session builds its ingestion; Session 15 adds the answers.

---

## Business scenario

Orbital Logistics' on-call engineers lose time at 3 a.m. searching runbooks, policies and postmortems for the one paragraph they need. The IT operations team wants an **Internal Knowledge Assistant**: ask a question, get an answer grounded in the documentation, with the sources it came from.

Before anything can be answered, the documents have to be in a searchable index, and they keep changing: runbooks are edited after every incident, policies are replaced, postmortems are added. Engineers save half-finished files. The index has to keep up, cheaply, every night, without anyone watching it.

Your job this week is that ingestion pipeline: a command that makes the index match the documents folder, does only the work that changed, survives broken files, and never writes a document's contents to a log.

## Learning objectives

By completing this assignment you will:

- **Design** the ingestion side of a RAG application, and **justify** its module boundaries in writing.
- **Implement** idempotent ingestion of Markdown and PDF files with content hashes, so that a second run does no work.
- **Persist** chunks, metadata and embeddings in a local Chroma database, and **replace** a document's chunks correctly when it changes or shrinks.
- **Handle** corrupt, empty, non-UTF-8 and scanned files per file, without losing the previous version or the other files.
- **Log** what ingestion does without leaking document contents, and **test** that it doesn't.

## Prerequisites

- Sessions 11 and 13: retrieval building blocks, and the AI-assisted workflow.
- The course environment's model cache: if you ran Session 11's workbook, the embedding model is already downloaded. Otherwise the first real run downloads about 67 MB.
- Git, and a terminal in a folder outside the course repository (as in earlier projects).

> **Rules for AI-assisted milestones.** Plan before you implement, keep each step small, run the tests yourself, and review every diff. The acceptance tests are the specification: never let an assistant edit `tests/acceptance/` or `tests/conftest.py`. If it proposes to, that's a finding for your reflection.

---

## Project setup

```bash
# macOS / Linux / Git Bash
cp -r ~/python-ai-engineering-bridge/projects/04-rag-capstone/starter ~/skillup/knowledge-assistant

# PowerShell
Copy-Item -Recurse ~\python-ai-engineering-bridge\projects\04-rag-capstone\starter ~\skillup\knowledge-assistant
```

```bash
cd ~/skillup/knowledge-assistant
git init
git add .
git commit -m "Project 04 starter"
git tag starter
uv sync
uv run pytest
```

All 72 tests fail with `NotImplementedError`, as expected.

| File | Status |
|---|---|
| `models.py` | `Document`, `Chunk` (with its stable `id`), `Hit`, `IndexConfig`, `IngestReport`. Provided: read it first |
| `errors.py`, `settings.py`, `embedding.py` | Provided. `embedding.py` has the `Embedder` protocol, `HashingEmbedder` (tests) and `FastEmbedEmbedder` (real use) |
| `cli.py` | Provided: `ingest [--rebuild]`, `status` and `search`. It works as soon as your modules do |
| `documents.py` | **Yours** (Milestone 2) |
| `chunking.py` | **Yours** (Milestone 3) |
| `store.py` | **Yours** (Milestone 4) |
| `ingestion.py` | **Yours** (Milestone 5) |
| `tests/conftest.py`, `tests/acceptance/` | Provided; don't edit |
| `data/docs/` | 24 synthetic documents in four folders, including three PDFs; `README.txt` explains them |

---

## Requirements

Each stub's docstring is the precise contract, and its test file is the executable version. In summary:

| # | Requirement | Where | Tests |
|---|---|---|---|
| R1 | Find every `.md` and `.pdf` under the folder, including subfolders, case-insensitively, skipping names that start with `.`. Each file's **source** is its relative path with `/` separators | `discover` | `test_documents.py` |
| R2 | A file's fingerprint is the SHA-256 of its bytes | `content_hash` | `test_documents.py` |
| R3 | Load Markdown as UTF-8 (ignoring a byte-order mark) with its title, and PDFs page by page. Raise `DocumentError` naming the source, and never quoting the file, for files that are empty, not UTF-8, corrupt or without text | `load_document` | `test_documents.py` |
| R4 | Chunks of at most `size` characters, split at `## ` sections first, with overlap, with headings as metadata rather than text, PDF pages kept apart, no text lost, indexes from 0 | `chunk_document` | `test_chunking.py` |
| R5 | A persistent Chroma index that stores every chunk field, including `None` ones, records its `IndexConfig`, and refuses a different one unless rebuilt | `ChunkStore.__init__` | `test_store.py` |
| R6 | `replace` makes the given chunks a source's **only** chunks; it validates its input before changing anything | `ChunkStore.replace` | `test_store.py` |
| R7 | `sources`, `chunks`, `remove`, `count` and `search` (cosine similarity, best first) | `ChunkStore` | `test_store.py` |
| R8 | Ingestion skips unchanged files entirely, replaces changed ones, adds new ones, removes deleted ones, and reports each | `ingest` | `test_ingestion.py` |
| R9 | A broken file is reported and keeps its previous chunks; other files carry on. Any other exception stops the run without leaving a file half-indexed | `ingest` | `test_ingestion.py` |
| R10 | Logs name sources (INFO for changes, WARNING for failures), never document text or full paths | `ingest` | `test_ingestion.py` |

`test_cli.py` runs the whole pipeline through the provided command line.

---

## Implementation milestones

### Milestone 1: Design

Before writing code, read `models.py`, `embedding.py`, `cli.py` and the four stubs. Then create `ARCHITECTURE.md` in the project root with these sections, in your own words:

1. **Modules.** For each of the eight modules: what it's responsible for, and its one reason to change.
2. **One changed file.** Walk through what happens, module by module, when `runbooks/vpn-outage.md` has been edited since the last run. Which calls are made, in which order, and what's in the index at each step?
3. **Decisions.** Your answer, with a reason, to each of:
   - How do you decide that a file is unchanged? What *doesn't* that decision cover?
   - What happens in the index when a previously indexed file can't be read?
   - In `replace`, do you delete first or write first? What does a search see if the process dies between the two steps?
   - How will you chunk: port your Session 11 code, or use `langchain-text-splitters` (already a dependency)? Why?
   - What will you log, at which level?
4. **Known limitations.** At least two. (You'll add to this list as you go.)

Commit it. You'll revise it in Milestone 6, and you'll present it in Session 16.

### Milestone 2: Documents

Implement `discover`, `content_hash` and `load_document`.

```bash
uv run pytest tests/acceptance/test_documents.py
```

- `Path.rglob`, `Path.relative_to` and `PurePath.as_posix` cover R1. Test on your own machine: on Windows, `str(relative)` has backslashes.
- `hashlib.file_digest` reads a file in blocks (notebook Part 1).
- `encoding="utf-8-sig"` reads UTF-8 and drops a byte-order mark if there is one. Files saved by Windows Notepad often start with one.
- pypdf raises `PdfReadError` (and subclasses) for corrupt files. Translate exactly that, plus `OSError`, into `DocumentError`; don't catch `Exception` (notebook Part 5).

### Milestone 3: Chunking

Implement `chunk_document`.

```bash
uv run pytest tests/acceptance/test_chunking.py
```

Two reasonable routes:

- **Port your Session 11 `split_sections` and `split_text`.** You know exactly how they behave, and they're tested.
- **Use `langchain-text-splitters`:** `MarkdownHeaderTextSplitter` for the sections and `RecursiveCharacterTextSplitter` for size and overlap. Less code to maintain, but check what it actually does before you rely on it: which headings it strips, whether it trims whitespace, how it measures size. Run it on one runbook in a Python shell and look.

Either way, the tests check behaviour, not implementation: size limits, sections, pages, overlap, and that no word of the document is lost.

### Milestone 4: The store

Implement `ChunkStore` over Chroma, the only module that imports `chromadb`.

```bash
uv run pytest tests/acceptance/test_store.py
```

- Open the database with `chromadb.PersistentClient(path=..., settings=ChromaSettings(anonymized_telemetry=False))`, and the collection with cosine distance and `embedding_function=None` (you supply the vectors), as in Session 11's notebook 03.
- Record the `IndexConfig` in the collection's metadata, and compare it yourself on every open. Remember notebook Part 3: `get_or_create_collection` ignores metadata for an existing collection.
- `None` can't be stored in Chroma metadata. Leave those fields out when writing, and read them back with `.get()`.
- `replace` is the heart of R6: an edited document must not keep old chunks, whether it grew or shrank. Notebook Part 2 shows what `add` and `upsert` alone get wrong. Decide your order of operations (Milestone 1) and write it in a comment.
- Chroma returns cosine **distance**; `Hit.score` is **similarity**.

### Milestone 5: Ingestion

Implement `ingest`.

```bash
uv run pytest tests/acceptance/test_ingestion.py
```

Follow the docstring and the flow diagram in the notebook. The tests check what the index **contains** after each scenario, and they count embedding calls, so "it ran without errors" isn't enough. A few tests deserve a close read before you start:

- `test_a_second_run_changes_nothing_and_embeds_nothing`: zero embedding calls on an unchanged folder.
- `test_an_embedder_failure_stops_the_run_but_loses_nothing`: an embedder that fails half-way, then a run that recovers.
- `test_logs_never_contain_document_text_or_full_paths`: the canary from notebook Part 6.

Then write **at least three tests of your own** in `tests/unit/`, for behaviour you decided in Milestone 1 that the acceptance tests don't pin down (for example: your order of operations in `replace`, a helper you wrote, or what your logs say about a removed file).

### Milestone 6: Run it for real

The real embedder, the real corpus, and the provided CLI. Run each step and keep the output for your deliverables:

```bash
uv run knowledge-assistant ingest                 # first run: downloads the model if needed
uv run knowledge-assistant ingest                 # second run
uv run knowledge-assistant status
uv run knowledge-assistant search "How do I promote the orders database replica?"
```

The first run indexes 24 files (94 chunks with the default settings, if you chunk the same way as the reference; your number may differ). The second run should report `24 unchanged` and finish in a couple of seconds, most of which is loading the model.

Now break things on purpose, one at a time, running `uv run knowledge-assistant -v ingest` after each:

1. Edit a runbook: add a `## Contacts` section. Only that file is updated.
2. Delete `guides/phishing-response.md`. It's removed.
3. Save a PDF with garbage in it: `echo "not a pdf" > data/docs/policies/broken.pdf`. It's reported, the exit code is 1, and the others carry on.
4. Set `ASSISTANT_CHUNK_SIZE=500` in `.env` and run again. It's refused with exit code 2. Rebuild with `ingest --rebuild`.
5. Restore the documents with `git checkout -- data/docs` and `git clean -f data/docs` (check what `git clean -n data/docs` would delete first). Remove the `ASSISTANT_CHUNK_SIZE` line from `.env`, and run `ingest --rebuild` once more.

Update `ARCHITECTURE.md` with anything that surprised you, then commit and tag:

```bash
git tag session-14
```

---

## Acceptance criteria

- `uv run pytest` passes: all 72 acceptance tests, plus your own unit tests.
- `uv run ruff check .` and `uv run ruff format --check .` are clean.
- A second `ingest` over an unchanged folder reports every file unchanged, and embeds nothing.
- Every scenario in Milestone 6 behaves as described, and you can explain why.
- `ARCHITECTURE.md` covers the four sections of Milestone 1, revised after Milestone 6.
- No document text appears in any log output, at any level.

## Testing

| Command | Expected |
|---|---|
| `uv run pytest tests/acceptance/test_documents.py` | 20 passed (Milestone 2) |
| `uv run pytest tests/acceptance/test_chunking.py` | 12 passed (Milestone 3) |
| `uv run pytest tests/acceptance/test_store.py` | 17 passed (Milestone 4) |
| `uv run pytest tests/acceptance/test_ingestion.py` | 17 passed (Milestone 5) |
| `uv run pytest` | 72 passed, plus yours |

The whole suite runs in about 15 seconds with the hashing embedder. Nothing in it needs the network, a model download or an API key.

## Debugging guidance

| Symptom | Where to look |
|---|---|
| `test_discover_uses_forward_slashes...` fails on Windows only | You built sources with `str()` on a path. What does `as_posix()` do? |
| A store test fails with `KeyError: 'page'` or `'section'` | Notebook Part 3, and quiz Q4 |
| `TypeError: ... Cannot convert Python object to MetadataValue` | A `None` value reached Chroma's `add` |
| `test_replace_with_fewer_chunks_leaves_no_old_ones_behind` fails | Notebook Part 2: positions that no longer exist still have chunks |
| `test_reopening_with_other_settings_is_refused` fails | Is the configuration you compare the one you **passed**, or the one the collection **recorded**? Print both |
| `ValueError: An instance of Chroma already exists for ... with different settings` | Two `PersistentClient`s for one folder in one process must use the same settings. Create clients in one place |
| The second run still embeds files | Print the hash you compare against and the hash you stored. Are they for the same source string? |
| `test_an_embedder_failure...` fails | Quiz Q3: what does the index hold while the embedder is running? |
| The logging test fails on the canary | Search your code for `chunk.text`, `document.text`, `path` and `{error}` in log calls. Then remember that libraries log too (notebook Part 6) |
| An assistant's code passes most tests but fails one "flaky" test | Run it three times. A test that depends on dictionary or folder order is telling you something; it isn't flaky |

Work through failures with **Observe → Hypothesize → Inspect → Fix → Verify**: read the assertion, guess the cause, print the evidence, fix one thing, run the test again.

## Extension challenges (optional)

1. **A pipeline version.** Add a `pipeline_version` to the configuration you record, and bump it when you change the loader or chunker, so that your own code changes trigger a rebuild like settings changes do. Which file has to change, and which tests?
2. **A dry run.** Add `ingest --dry-run`, which reports what *would* be added, updated, removed and skipped, without loading or embedding anything. What's the minimum work it has to do?
3. **OpenAI embeddings.** Add an `OpenAIEmbedder` using `text-embedding-3-small` (the course's default provider, decision D3), with the key from `.env`. It costs money per token: count the tokens first, and test it with an HTTP-level fake as in Session 09. What happens to an existing index when you switch?
4. **Batching.** A 3,000-file corpus means many embedding calls. Embed in batches of up to N chunks across files, without breaking R9. Where does the risk move?
5. **Another format.** Add `.txt` support. Which modules change, and which don't? (If more than two change, revisit your boundaries.)

## Reflection

Answer in `ARCHITECTURE.md`, or in a separate `REFLECTION.md`:

1. Which of your module boundaries would you defend in a design review, and which would you change now that the code exists?
2. A second run embeds nothing. What exactly makes that true, and what would silently break it?
3. If you used an assistant: where did it help most, and what did it get wrong? Did it ever propose changing the acceptance tests, catching `Exception`, or logging chunk text?
4. Your store keeps or deletes a broken file's chunks (your Milestone 1 decision). Who would disagree with that choice, and why?
5. What is the slowest part of a first run, and of a second run? How did you find out?

## Deliverables

Submit your `knowledge-assistant` repository, tagged `session-14`, containing:

- Your implementations of `documents.py`, `chunking.py`, `store.py` and `ingestion.py`.
- At least three tests of your own in `tests/unit/`.
- `ARCHITECTURE.md`, revised after Milestone 6, with your reflection.
- The output of the Milestone 6 runs (paste it into `ARCHITECTURE.md`, or save it as `RUNS.md`).

Don't commit the `index/` folder or `.env`: the starter's `.gitignore` already excludes them.

---

<!-- skillup-branding:start -->
## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center">
  <img src="../../../assets/diagrams/SkillUpWithSanjay.png" alt="#SkillUpWithSanjay logo" width="60">
</p>

<p align="center">
  <strong>#SkillUpWithSanjay</strong><br>
  <a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>
  &nbsp;&middot;&nbsp;
  <a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
</p>
<!-- skillup-branding:end -->
