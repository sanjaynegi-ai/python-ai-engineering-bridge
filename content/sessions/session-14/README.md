# Session 14: RAG Capstone, Ingestion

**Phase 4: AI-Assisted Engineering and RAG Capstone**

## Session overview

This session starts the capstone: the **Internal Knowledge Assistant**, a RAG application that answers questions about Orbital Logistics' IT documentation, with sources. Over Sessions 14 to 16 you build it, extend it and present it.

This week is **ingestion**. Session 11 taught every building block (loading, chunking, embedding, a vector store); the capstone turns them into software that runs every night without supervision. That means doing only the work that changed, replacing edited documents correctly, surviving broken files, recording how the index was built, and never logging a document's contents. You design the module boundaries first, then build the pipeline against 72 acceptance tests, with an AI assistant if you choose.

## Why this matters

Most RAG demos end at "it answered one question". Production systems fail in the places a demo never visits: a runbook edited yesterday still answering with last month's text, a deleted policy that keeps being cited, a nightly job that re-embeds 3,000 files for one typo, a corrupt PDF that stops the whole run, or a log that copies confidential documents into a central log store.

Ingestion is where those problems are cheapest to prevent. The habits involved (content fingerprints, idempotent writes, failure isolation, safe logging) aren't specific to AI: they're the same ones behind every reliable sync job, cache or ETL pipeline you've worked on. This session applies them in Python, with a vector database.

## Prerequisites

**Knowledge:** Sessions 01–13, especially Session 11 (chunking, embeddings, Chroma), Session 04 (packages and tests), Session 09 (protocols and fakes) and Session 13 (the AI-assisted workflow).

**Setup:**

- The course environment, up to date: `uv sync` in the course repository.
- The embedding model from Session 11, already cached, or about 67 MB to download on the first real run. The tests never need it.
- Claude Code or an approved assistant, if you use one for the AI-assisted milestones.

## Learning objectives

By the end of this session you will be able to:

1. **Design** the capstone's ingestion architecture, and **justify** each module boundary by its reason to change.
2. **Implement** idempotent ingestion of Markdown and PDF files using content hashes, so that a second run does no work.
3. **Persist** chunks, metadata and embeddings in a local Chroma database, and **replace** a document's chunks correctly when it is edited, shortened or deleted.
4. **Handle** corrupt, empty, non-UTF-8 and scanned files per file, without losing other files or a document's previous version.
5. **Log** ingestion without leaking document contents, and **test** that with a canary.


## Concepts covered

| Concept | Depth |
|---|---|
| Capstone architecture and module boundaries | Guided integration |
| Content hashing (`hashlib.file_digest`) versus modification times | Independent implementation |
| Stable chunk IDs; `add`, `upsert` and replace in Chroma | Guided integration |
| Chroma metadata: `None` values, collection metadata | Working knowledge |
| Recording the index configuration; rebuilds | Guided integration |
| Per-file failure isolation; the order of operations | Independent implementation |
| Logging without leaking; canary tests | Independent implementation |
| `Protocol`-based boundaries and fakes for testing | Independent implementation |



## Guided exercises

- **Notebook Part 1, Predict:** does a CRLF copy of a file have the same hash? What does that cost?
- **Notebook Part 2, Challenge:** "delete then add" versus "upsert then delete the leftovers": what does a search see if the process dies in between?
- **Notebook Part 5, Modify:** narrow `except Exception` and watch the real bug surface.
- **Milestone 1 in pairs:** compare your module responsibilities and your three decisions. Where do you disagree, and what would settle it?

## Independent assignment

[`workbook/assignment.md`](workbook/assignment.md): **Capstone ingestion.** Copy the Project 04 starter, design the pipeline in `ARCHITECTURE.md` (Independent), then implement `documents.py`, `chunking.py`, `store.py` and `ingestion.py` against 72 acceptance tests (AI-assisted), add your own tests, and run the pipeline for real, breaking it on purpose.

## Expected deliverables

- Your `knowledge-assistant` repository, tagged `session-14`, with all 72 acceptance tests passing and Ruff clean.
- At least three unit tests of your own.
- `ARCHITECTURE.md`: modules, the path of one changed file, your decisions, known limitations, and your reflection.
- The output of the Milestone 6 runs.

## Common mistakes

| Mistake | Consequence | Better |
|---|---|---|
| Re-embedding every file on every run | Slow, and costly with a paid embedding API | Skip files whose content hash matches the index |
| Random chunk IDs | The index doubles on every run | IDs from source and position |
| Relying on `add` or `upsert` alone | Edits never land, or shortened documents keep stale chunks | Make the new chunks the source's only chunks |
| Not removing deleted files | Deleted policies keep answering questions | Remove sources that are no longer on disk |
| Comparing only content hashes | A new model or chunk size changes nothing | Record the configuration; refuse or rebuild |
| Storing `None` in Chroma metadata | `TypeError` from `add`; missing keys after `upsert` | Leave `None` out, read with `.get()` |
| `except Exception` around each file | Your own bugs are reported as bad documents | Catch `DocumentError` only |
| Deleting before embedding | An embedder outage erases a document | Embed first, then replace |
| Logging chunk text or full paths | Document contents and usernames in log storage | Log sources and counts; test with a canary |

## Reading resources

[`resources/references.md`](resources/references.md): `hashlib`, `pathlib` and `logging`; Chroma's add, update, delete and metadata-filtering pages; pypdf's errors; the LangChain text splitters; and further reading on idempotent pipelines.

## Reflection questions

1. Which inputs decide what's in your index, and which of them does a content hash cover?
2. Your ingestion keeps a broken file's previous chunks, or deletes them. Who is better served by that choice, and who isn't?
3. Where in your pipeline could a document's text reach a log, including through code you didn't write?
4. If the corpus grew from 24 files to 24,000, which part of your design would hurt first?
5. If you used an assistant: which of its suggestions did you reject, and why?

## Interview questions

1. "How do you keep a vector index in sync with a document store that changes daily?"
2. "A user edited a document, but the RAG system still answers with the old text. How would you investigate?"
3. "Why might you prefer a content hash over a modification time to detect changes? When would you use both?"
4. "You've changed your chunking strategy. What has to happen to the existing index, and how do you make sure it does?"
5. "How do you stop a nightly ingestion job from failing on one bad file, without hiding real bugs?"
6. "How would you test that a pipeline never logs sensitive content?"

## Next-session preparation

**Session 15: RAG capstone, application** answers questions from the index you built: retrieval, a grounded prompt, an LLM answer with sources, "not found in the sources" for unanswerable questions, a FastAPI service, a Streamlit UI, and a small evaluation set.

Before continuing:

- Finish this workbook, with all 72 tests passing, and tag `session-14`.
- Run `knowledge-assistant ingest` with the real embedder, so your index is ready.
- Check that your LLM key from Session 09 still works. Session 15's tests won't need it, but the real assistant will.
- Reread Session 11's `build_context` and `cited_numbers`, and Session 09's structured-output validation: next week combines them.

---

<!-- skillup-branding:start -->
## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center">
  <img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="#SkillUpWithSanjay logo" width="60">
</p>

<p align="center">
  <strong>#SkillUpWithSanjay</strong><br>
  <a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>
  &nbsp;&middot;&nbsp;
  <a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
</p>
<!-- skillup-branding:end -->
