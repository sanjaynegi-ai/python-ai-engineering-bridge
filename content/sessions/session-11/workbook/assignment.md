# Session 11 Assignment: Search the IT Handbook

**Type:** Independent. Complete this without an AI coding assistant; Session 13 covers AI-assisted work.
**Estimated time:** 2.5–3 hours
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb), [`03-building-a-vector-store.ipynb`](../notebooks/03-building-a-vector-store.ipynb), and the settings, CLI and testing patterns from Sessions 05–06
**Project:** `handbook-search`, a standalone project. The RAG capstone (Sessions 14–16) builds on the same ideas.

---

## Business scenario

The IT operations team at Orbital Logistics keeps its runbooks and policies in a folder of Markdown files and PDFs. On-call engineers search it with `grep`, and they regularly miss the right runbook because they use different words from the author: "the VPN keeps dropping" against a runbook titled "Office VPN Problems".

Before anyone puts an LLM in front of this handbook, the team lead wants to know whether **retrieval** works: given a question, does the right passage come back, with a source an engineer can open? And when the handbook doesn't cover a question, does the tool say so rather than return something that only sounds related?

You'll build the retrieval half of a RAG application as a command-line tool, and measure how well it works with a small evaluation set.

## Learning objectives

By completing this assignment you will:

- **Implement** document loading for Markdown and PDF files that reports problem files instead of crashing.
- **Implement** chunking that keeps each chunk's source, title, section, page and position.
- **Implement** a persistent vector store with cosine-similarity search, metadata filtering, and a check against mixing embedding models.
- **Validate** model citations against the sources that were actually provided.
- **Measure** retrieval with hit rate and rejection rate, and **tune** chunk size and the minimum score with evidence.
- **Debug** a retrieval failure with the Observe → Hypothesize → Inspect → Fix → Verify workflow.

## Prerequisites

- The Session 11 concepts notebook and the vector-store notebook.
- About **70 MB** of free disk space and a network connection the first time you run `ingest` with the real embedding model. It's downloaded once into `~/.cache/fastembed` (or your `FASTEMBED_CACHE_PATH`); after that, everything runs offline.
- No API key. Nothing in this assignment calls a paid API.

---

## Project setup

Copy the starter project out of the course repository, adjusting the source path to where you cloned the course:

```bash
# macOS / Linux / Git Bash
cp -r ~/python-ai-engineering-bridge/sessions/session-11/workbook/starter ~/skillup/handbook-search

# PowerShell
Copy-Item -Recurse ~\python-ai-engineering-bridge\sessions\session-11\workbook\starter ~\skillup\handbook-search
```

Then:

```bash
cd ~/skillup/handbook-search
git init
git add .
git commit -m "handbook-search starter"
git tag starter
uv sync
uv run pytest
```

**2 tests pass and the rest fail or error.** That's expected: the two that pass exercise code that's already provided. Read the starter's `README.md`, then the files below.

| File | Status |
|---|---|
| `models.py`, `errors.py`, `settings.py` | Provided. Read them; you shouldn't need to change them |
| `embedding.py` | Provided: the `Embedder` protocol, a word-hashing embedder for tests, and the real fastembed model |
| `cli.py` | Provided: `ingest`, `query` and `evaluate`, built on the functions you write |
| `loading.py` | `load_markdown` provided; `load_pdf` and `load_documents` are yours |
| `chunking.py`, `store.py`, `retrieval.py` | Stubs. Yours |
| `evaluation.py` | `load_questions` and the result types provided; `evaluate` is yours |
| `tests/acceptance/`, `tests/conftest.py` | Provided. Don't edit |

The notebooks contain working versions of several of these pieces. You may reread them, but **write the package code yourself**: the specifications here differ from the notebooks in details (the PDF title, the problem list, the index format, the errors), and the tests check those details.

---

## Requirements

| # | Requirement |
|---|---|
| R1 | All 63 acceptance tests pass, unchanged. |
| R2 | One unreadable, non-UTF-8 or empty file never stops ingestion: it's reported, and the other files are indexed. |
| R3 | Every chunk can be cited: file name, plus section for Markdown or page for PDF. |
| R4 | The index refuses to load with a different embedding model, with a message that says what to do. |
| R5 | `query` prints `I can't find this in the handbook.` and exits `1` when nothing scores above `HANDBOOK_MIN_SCORE`. |
| R6 | With the default settings and the real model, `evaluate data/questions.jsonl` finds at least **10 of the 12** answerable questions and rejects **all 3** unanswerable ones. |
| R7 | `EVALUATION.md` records your measurements and the settings you chose (Milestone 7). |
| R8 | At least **8** test cases of your own in `tests/unit/`. |
| R9 | `uv run ruff check .` and `uv run ruff format --check .` pass. |

---

## Implementation milestones

### Milestone 1: Predict (10 min)

Open `data/questions.jsonl` and skim two or three handbook documents. In `NOTES.md`, predict:

1. Which question or questions retrieval is most likely to get **wrong**, and why.
2. Whether the `HashingEmbedder` used by the tests will find "The Berlin office VPN keeps disconnecting." in `runbook-vpn-outage.md`. What does it need for a match?
3. What should happen when someone edits a Markdown file after `ingest` and then runs `query`.

### Milestone 2: Loading (20 min)

Implement `load_pdf` and `load_documents` in `loading.py`, following their docstrings.

- A PDF gives one `Document` per page that has text, numbered from 1. Use `pypdf`'s `PdfReader`; the title comes from its `metadata`, which may be missing entirely or may have no title.
- `load_documents` reads only `.md` and `.pdf` files, in name order, and returns `(documents, problems)`. Each problem is a short message that starts with the file name.

```bash
uv run pytest tests/acceptance/test_loading.py
```

### Milestone 3: Chunking (35 min)

Implement the three functions in `chunking.py`. The docstrings are the specification; the tests show the edge cases.

- `split_sections` splits Markdown at `## ` headings.
- `split_text` splits text into units (at line breaks, and after `.` `!` `?` `:` followed by whitespace) and packs them into pieces of at most `size` characters. Each new piece starts with the previous piece's last units, as many as fit in `overlap` characters.
- `chunk_documents` puts it together and numbers the chunks per file.

Before running the tests, work through `test_split_text_overlaps_neighbours` on paper: which pieces do you expect?

```bash
uv run pytest tests/acceptance/test_chunking.py
```

### Milestone 4: The vector store (35 min)

Implement `VectorStore` in `store.py`. Use NumPy, as in the vector-store notebook; you choose how to keep the vectors and chunks internally.

- `add` normalises vectors as it stores them, and rejects mismatched counts or dimensions with `ValueError`.
- `search` returns `Hit`s, best first. Filter by `source` **before** taking the top `k`.
- `save` writes exactly two files, `vectors.npy` and `store.json`; `load` turns every way the index can be missing or damaged into `SearchIndexError`.

```bash
uv run pytest tests/acceptance/test_store.py
```

### Milestone 5: Retrieval and citations (15 min)

Implement `retrieve`, `build_context` and `cited_numbers` in `retrieval.py`. `build_context` produces the numbered sources you would put into an LLM prompt; `cited_numbers` checks an answer's `[n]` citations against them, as in Part 5 of the concepts notebook.

```bash
uv run pytest tests/acceptance/test_retrieval.py
```

### Milestone 6: Evaluation, end to end (15 min)

Implement `evaluate`, then run the whole tool with the real model:

```bash
uv run pytest
uv run handbook-search ingest
uv run handbook-search query "The Berlin office VPN keeps disconnecting."
uv run handbook-search evaluate data/questions.jsonl
```

The first `ingest` downloads the model. Check your Milestone 1 predictions against the evaluation output.

### Milestone 7: Measure, debug and tune (35 min)

Record everything in `EVALUATION.md`.

1. **Baseline.** Note the hit rate, rejection rate and missed questions with the default settings. Then try the hashing embedder (`HANDBOOK_EMBEDDER=hashing`, ingest again) with `HANDBOOK_MIN_SCORE` at `0.6` and at `0.2`. What does the comparison tell you about word matching and meaning?
2. **Debug one miss.** Pick a question that went wrong, and work through **Observe → Hypothesize → Inspect → Fix → Verify**:
   - *Observe:* which chunks came back, with which scores? (`query` prints both.)
   - *Hypothesize:* is the answer in the handbook at all? In which chunk? Is it a chunking problem, a vocabulary problem, or a threshold problem?
   - *Inspect:* find the chunk that should have matched, and its score. `index/store.json` is readable JSON.
   - *Fix:* try one change at a time: chunk size, overlap, `top_k`, or what goes into the embedded text. **Don't** edit the handbook or the questions to make the miss disappear.
   - *Verify:* run the evaluation again. Did the fix help that question **and** keep the others working?

   A fix you tried that didn't work is a valid result, if you can explain why it didn't.
3. **Chunk size.** Evaluate with `HANDBOOK_CHUNK_SIZE` at 250, 500 and 1000 (with overlap at about a fifth of the size). Record the number of chunks and both rates for each.
4. **Minimum score.** For the three unanswerable questions and the lowest-scoring answerable question, record the top score. Where would you set `HANDBOOK_MIN_SCORE`, and how much margin is there?
5. **Your own questions.** Add **at least five** questions to `data/questions.jsonl`: three answerable ones phrased the way a stressed on-call engineer would ask, and two the handbook doesn't answer but which sound close to something it does. How does your tool do?

End with the settings you'd ship, and why.

### Milestone 8: Your own tests (25 min)

Create `tests/unit/` with at least **8** test cases that cover behaviour the acceptance tests don't. Ideas:

- A Markdown file without a `# ` title line, or with an empty first line.
- `## ` inside a fenced code block: what does your `split_sections` do? Decide whether that's acceptable, and test the behaviour you chose.
- A chunk is never empty, and never only whitespace.
- `search` with `k` larger than the number of chunks, or with every chunk below `min_score`.
- Two chunks with exactly the same score come back in a stable order.
- `save` into a folder that doesn't exist yet; `save` twice into the same folder.
- `cited_numbers` with `[12]` when there are two sources, or with text like `[note]`.
- `evaluate` with an empty question list.

As before, **prove that two of your tests can fail**: break the code they cover, record the failure in `NOTES.md`, and restore it.

### Milestone 9: Quality gate (5 min)

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
git status          # index/ must not appear: it's generated, and git-ignored
git add .
git commit -m "Session 11: handbook search"
git tag session-11
```

---

## Acceptance criteria

| Check | Expected result |
|---|---|
| `uv run pytest tests/acceptance` | `63 passed`, with no network and no model download |
| `uv run pytest tests/unit` | At least 8 test cases of your own pass |
| `uv run handbook-search ingest` | `Indexed N chunks from 12 files into index`; exit code `0` |
| `uv run handbook-search evaluate data/questions.jsonl`, using the original 15 questions | At least 10 of 12 answerable questions found, and 3 of 3 rejected |
| `uv run handbook-search query "What's for lunch?"` | `I can't find this in the handbook.`; exit code `1` |
| After `ingest`, `HANDBOOK_EMBEDDER=hashing uv run handbook-search query "VPN"` | A one-line error naming both models and telling you to ingest again; exit code `2` |
| `git diff starter -- tests/acceptance tests/conftest.py` | No output |
| `git ls-files index` | No output |
| `uv run ruff check .` and `uv run ruff format --check .` | Both pass |
| `EVALUATION.md` and `NOTES.md` | Measurements, the debugging walk-through, your chosen settings, predictions and reflection |

In PowerShell, set the variable for one command like this: `$env:HANDBOOK_EMBEDDER = "hashing"; uv run handbook-search query "VPN"; Remove-Item Env:HANDBOOK_EMBEDDER`.

## Debugging guidance

| You see | Where to look |
|---|---|
| `test_pdf_title_falls_back_to_the_file_name` fails with `AttributeError` or a title of `None` | A PDF can have no metadata at all, or metadata without a title. Handle both. |
| `test_damaged_pdf_raises_document_error` fails with a `pypdf` exception | Catch `pypdf`'s errors and raise `DocumentError` with the file name, chaining the original with `from`. |
| `test_folder_loads_markdown_and_pdf_in_name_order` counts 12, not 13 | The count is of documents, not files: a two-page PDF gives two. |
| A broken file stops `load_documents` with `UnicodeDecodeError` | `read_text` raises it for non-UTF-8 bytes; it isn't a `DocumentError`. |
| pytest hangs in a `split_text` test | The carried overlap plus the next unit doesn't fit, so the loop never advances. A new piece must always make progress. |
| `test_split_text_respects_the_size` finds pieces a few characters too long | Check how you measure length: units are joined with single spaces, and the spaces count. |
| Chunk indexes restart at 0 on each PDF page | Count per source file, not per document. |
| `test_vectors_are_normalised_when_added` scores above 1 | Normalise the query as well as the stored vectors. |
| `test_source_filter_is_applied_before_ranking` returns `[]` | You took the top `k` first and filtered afterwards. |
| `test_load_a_damaged_index` gets `JSONDecodeError` | Turn it into `SearchIndexError`. Which other exceptions can `np.load` and `Chunk(**fields)` raise? |
| With the hashing embedder, `evaluate` finds almost nothing | Its scores are much lower than the real model's, so the default `HANDBOOK_MIN_SCORE` of `0.6` filters out nearly everything. A threshold belongs to one embedding model. |
| After changing a setting, `evaluate` gives exactly the same numbers as before | Did you run `ingest` again? Chunk settings and the embedder only take effect at ingest time. (Identical numbers can also be a genuine result: check the chunk count `ingest` prints.) |
| `query` finds the right file, but the wrong passage | Inspect the chunk boundaries for that file in `index/store.json`: the answer may be split across two chunks. |

## Extension challenges (optional)

1. **Incremental ingest.** Store a hash of each file's bytes in `store.json`, and on `ingest` re-embed only the files that changed, were added, or were removed. Test it with a file you edit between two ingests.
2. **Filter from the command line.** Add `query --source FILE` using `search(source=...)`, and an error with exit code `2` for a file name that isn't in the index.
3. **Chroma.** Implement a `ChromaStore` with the same `add`/`search` interface (the vector-store notebook, Part 5), and run the acceptance tests for the store against both. Which tests don't fit, and why?
4. **Keyword fallback.** Combine the cosine score with a simple keyword score for exact tokens such as `P2` or `db-03`. Does it fix the P2 question without breaking the rejection rate? Measure it.
5. **Answer generation.** Send `build_context(hits)` and the question to an LLM with your Session 09 client, and check the answer's citations with `cited_numbers`. Keep it behind an option, and mock it in tests.

## Reflection

Answer briefly in `NOTES.md`:

1. How close were your Milestone 1 predictions?
2. What did the evaluation tell you that reading a few query results wouldn't have?
3. Your evaluation set has 15 to 20 questions. What could go wrong if you tuned `HANDBOOK_MIN_SCORE` until it scored 100% on exactly this set?
4. Why does the index store the embedding model's ID? What would happen without the check?
5. Compare this pipeline with a search feature you've built or used before, such as SQL `LIKE`, Elasticsearch, or Lucene. What does embedding-based retrieval do better, and what does it do worse?

## Deliverables

Submit **one** of the following, as your course instructions specify:

- a link to a Git repository containing the project, with the `session-11` tag (push only to a repository you own; keep it private if you prefer), **or**
- a `.zip` of the project folder **without** `.venv/` and `index/`.

The submission must include:

- [ ] `loading.py`, `chunking.py`, `store.py`, `retrieval.py` and `evaluate` implemented
- [ ] `tests/acceptance/` and `tests/conftest.py` unchanged, and your `tests/unit/` with at least 8 test cases
- [ ] `data/questions.jsonl` with your additional questions
- [ ] `EVALUATION.md` with your measurements, debugging walk-through and chosen settings
- [ ] `NOTES.md` with your predictions, the two failing-test proofs, and the reflection
- [ ] All acceptance criteria passing
