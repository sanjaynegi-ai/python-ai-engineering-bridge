# Session 11: Retrieval and RAG Fundamentals

**Phase 3: Python for AI Applications**

## Session overview

An LLM knows nothing about your company's runbooks, policies or last month's postmortem. **Retrieval-augmented generation (RAG)** fixes that without retraining anything: before asking the model, search your own documents for the passages that answer the question, put them in the prompt as numbered sources, and require the answer to cite them.

This session builds that pipeline from plain Python, so nothing is hidden: loading Markdown and PDF files, chunking them while keeping their metadata, embedding the chunks with a free local model, searching them with cosine similarity in a vector store you build with NumPy, and constructing a grounded prompt with checkable citations. Then it does what most tutorials skip: it breaks retrieval on purpose, and measures it with an evaluation set.

The workbook builds `handbook-search`, the retrieval half of a RAG application, as a tested command-line tool.

## Why this matters

RAG is the most common way companies put LLMs to work on their own data, and most of its failures are **retrieval** failures: the right passage was never found, was cut in half, or lost its source along the way. Those are ordinary data-engineering problems, and they're where an experienced engineer adds the most value.

Building the pipeline by hand first means you'll understand what LangChain's loaders, splitters and retrievers do, and what a vector database adds, before you depend on them in the capstone (Sessions 14–16).

## Prerequisites

**Knowledge:** Sessions 01–10. In particular, files and JSON (Session 03), package structure and pytest (Session 04), settings with Pydantic (Session 06), and grounded prompts and structured output (Session 09).

Before you begin:

1. In the course repository, run `git pull` and `uv sync`. It adds a `rag` group to the notebook kernel: `pypdf`, `chromadb` and `langchain-text-splitters`. The environment grows by about 170 MB.
2. **Optional, but recommended:** download the embedding model before continuing, so a slow network doesn't interrupt the workbook. In Session 01's concepts notebook, Part 9, set `RUN_FASTEMBED = True` and run the cell. It downloads about 67 MB into `~/.cache/fastembed` (or your `FASTEMBED_CACHE_PATH`), once. The notebooks don't need the model (they use recorded vectors), but the workbook does, and it uses the same cache.
3. Finish the Session 10 workbook and tag it `session-10`.

## Learning objectives

By the end of this session you will be able to:

1. **Explain** retrieval-augmented generation, its ingestion and query phases, and what embeddings represent.
2. **Implement** loading of Markdown and PDF documents, reporting files that can't be read.
3. **Implement** chunking at document structure, then by size with overlap, keeping source, section and page for every chunk.
4. **Build** a cosine-similarity vector store with NumPy, persist it with its model's identifier, and **compare** it with Chroma.
5. **Construct** a grounded prompt with numbered sources, and **validate** the citations in an answer.
6. **Diagnose** retrieval failures: off-topic questions, wrong chunk sizes, missing metadata and garbled text.
7. **Evaluate** retrieval with hit rate and rejection rate, and **choose** a minimum score from evidence.


## Concepts covered

| Concept | Depth |
|---|---|
| RAG: ingestion and query phases; when RAG fits, and when it doesn't | Working knowledge |
| Loading Markdown and PDF (`pypdf`); problem files; scanned pages | Independent implementation |
| Chunking by structure and size; overlap; metadata for citations | Independent implementation |
| Library splitters (`langchain-text-splitters`) | Awareness |
| Embeddings and cosine similarity; normalisation | Working knowledge |
| A NumPy vector store: add, search, filter, save, load | Independent implementation |
| Embedding search compared with keyword search | Working knowledge |
| Grounded prompts with numbered sources; citation checks | Guided integration |
| Minimum score and "not found" | Independent implementation |
| Retrieval evaluation: hit rate, rejection rate, threshold choice | Guided integration |
| Chroma as an embedded vector database | Awareness |
| Indirect prompt injection through documents | Awareness |



## Guided exercises

1. [`notebooks/01-concepts.ipynb`](notebooks/01-concepts.ipynb) (offline by default; live embedding and LLM calls are opt-in):
   - **The shape of RAG:** the architecture diagram, and the two phases.
   - **Loading:** Markdown and PDF, and what can go wrong with PDF text.
   - **Chunking:** sections, sizes, overlap, metadata; library splitters.
   - **Retrieval:** embeddings, cosine similarity, keyword search for comparison.
   - **Grounded answers:** numbered sources, and checking citations.
   - **Failures:** off-topic questions, chunk sizes, missing metadata, garbled text.
   - **Evaluation:** hit rate, and choosing the minimum score.
2. [`notebooks/03-building-a-vector-store.ipynb`](notebooks/03-building-a-vector-store.ipynb): the vector store by hand, how brute force scales, persistence and the model check, metadata filtering, and the same with Chroma.
3. [`notebooks/02-practice-quiz.ipynb`](notebooks/02-practice-quiz.ipynb): 11 self-check questions.

## Independent assignment

[**Workbook: search the IT handbook**](workbook/assignment.md) (*Independent*: no AI coding assistant)

Build `handbook-search`, a command-line tool that ingests the handbook and returns the passages that answer a question, with their sources. Make 63 acceptance tests pass, then measure retrieval with the real embedding model, debug a miss, and choose your settings from the evidence.

## Expected deliverables

- The `handbook-search` project, tagged `session-11`.
- `uv run pytest` passing offline: 63 acceptance tests, unchanged, plus at least 8 of your own.
- `EVALUATION.md` with your measurements, a debugging walk-through and your chosen settings; `NOTES.md` with your predictions and reflection.

## Common mistakes

| Mistake | Instead |
|---|---|
| Embedding questions and chunks with different models | One model, with its identifier stored in the index and checked on load |
| No minimum score: every question gets results | A threshold chosen from evaluation questions, and an honest "not found" |
| Chunks without source, section or page | Keep metadata from loading onwards, so every answer can be cited |
| Fixed-size character chunks that cut sentences and mix sections | Split at structure first, then pack whole sentences |
| Indexing PDFs without looking at the extracted text | Inspect samples; report pages with no text |
| Filtering after taking the top `k` | Filter first, then rank |
| Trusting the model's citations | Check every cited number against the sources sent |
| Tuning on a handful of hand-picked questions | An evaluation set with answerable **and** unanswerable questions, and both rates |
| Putting retrieved text in the system message | Sources in the user message, marked as data |

## Reading resources

Curated official documentation for this session: [`resources/references.md`](resources/references.md).

## Reflection questions

1. Which retrieval failure from this session would be hardest to notice in production, and how would you detect it?
2. When would fine-tuning a model, or simply putting a whole document in the prompt, be a better choice than RAG?
3. How would you keep the index in sync with documents that change every day?
4. What would you need to change before indexing documents that not every employee is allowed to read?

## Interview questions

Practise answering these out loud and support each answer with clear engineering reasoning:

1. What is RAG, and what problem does it solve?
2. Walk me through what happens between a user's question and the answer in a RAG application.
3. How do you choose a chunk size? What goes wrong if chunks are too small, or too large?
4. What is an embedding, and why do we use cosine similarity to compare them?
5. How do you stop a RAG system from answering questions its documents don't cover?
6. How would you evaluate a RAG system? What would you measure first?
7. When would you use a vector database rather than an in-memory index?
8. What is indirect prompt injection, and how do you reduce the risk in RAG?

## Next-session preparation

**Session 12: Introduction to LangGraph** turns a straight-line pipeline into a small stateful workflow: typed state, nodes, edges and conditional routing. It finishes **Project 03** (`incident-triage`) with a validation-and-routing workflow.

Before continuing:

- Finish this workbook and tag `session-11`.
- Make sure your Session 10 `incident-triage` project still passes its tests: Session 12 builds on it.

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
