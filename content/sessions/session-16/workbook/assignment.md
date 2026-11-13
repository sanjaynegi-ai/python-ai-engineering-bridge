# Session 16 Assignment: Capstone Completion

**Type:** Part A (before the session) and Part B (the final assessment, in the session) are **Independent**. Part C (after the session) is **AI-assisted**: you may use Claude Code, or an approved assistant, following the Session 13 workflow.
**Estimated time:** 30 minutes before the session; about 3 hours after it
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb), and your `knowledge-assistant`, tagged `session-15`
**Project:** **Project 04**, the capstone. This assignment completes it: **Milestone 4**.

---

## Business scenario

The IT operations team wants to roll the Internal Knowledge Assistant out to every on-call engineer. Before they do, the platform team has two conditions: an end-to-end test suite that shows the parts work together when the documents change, and logs that let the on-call engineer for the assistant itself answer "is it slow, is it answering, and what happened to this request?" without reading anyone's question. And your team lead wants five minutes from you on how it works and where it's weak.

## Learning objectives

By completing this assignment you will:

- **Run** integration tests across the whole assistant, and **fix** what they reveal.
- **Implement** structured JSON logging with a request ID that links one request's lines.
- **Instrument** ingestion, answering and the API with events, and **answer** operational questions from the logs.
- **Present** your architecture, and **defend** its decisions and limitations.
- **Demonstrate**, in the final assessment, that you can do the core of the course on your own.

## Prerequisites

- Your `knowledge-assistant`, tagged `session-15`, with all 136 tests passing and a clean `git status`.
- `ARCHITECTURE.md` and `EVALUATION.md` from Sessions 14 and 15.

---

## Part A: Before the session (30 min, Independent)

You'll demonstrate your capstone in five minutes, from its `session-15` state. Create `PRESENTATION.md` with:

1. The problem, in one sentence.
2. A diagram of **your** modules and the path of one question. Text or Mermaid in the Markdown file is fine.
3. Two decisions you'd defend, each with the alternative you rejected and why.
4. What you'll show live: one answered question and one "not found" (offline mode is fine: `ASSISTANT_GENERATOR=extractive`), and one number from `EVALUATION.md`.
5. Two known limitations, and what you'd do about each.

Rehearse once against a timer. Notebook Part 5 has examples of weak and strong statements, and the [capstone rubric](../../../assessments/capstone-rubric.md) is what the demonstration is assessed against.

## Part B: In the session

- **The final assessment:** 60 minutes, without AI assistants. Read [`assessments/final-assessment.md`](../../../assessments/final-assessment.md) and work through the checklist in [`assessments/python-readiness.md`](../../../assessments/python-readiness.md) beforehand. Check that you can switch off your editor's AI features.
- **Demonstrations:** five minutes each, then questions.

---

## Part C: After the session, complete the capstone

### Project setup

Copy the Session 16 files over your project. There are no new dependencies.

```bash
# macOS / Linux / Git Bash
cp -r ~/python-ai-engineering-bridge/projects/04-rag-capstone/session-16/. ~/skillup/knowledge-assistant/

# PowerShell
Copy-Item -Recurse -Force ~\python-ai-engineering-bridge\projects\04-rag-capstone\session-16\* ~\skillup\knowledge-assistant\
```

```bash
cd ~/skillup/knowledge-assistant
git status
uv run pytest
```

The copy **replaces** the provided `cli.py` (it now configures logging, and has a `--log-format json` option) and **adds** `logging_setup.py` (partly yours), three test files and a `tests/integration/` folder. Because the new CLI calls `configure_logging()`, which you haven't written yet, **every test that goes through the CLI fails until Milestone 1 is done**, including Session 14's and 15's CLI tests. That's expected; commit and start with Milestone 1.

| File | Status |
|---|---|
| `logging_setup.py` | `REQUEST_ID` and `install_request_ids()` provided; **`JsonFormatter` and `configure_logging` yours** (Milestone 1) |
| `cli.py` | Provided, replaced |
| `tests/acceptance/test_logging_setup.py` | Milestone 1 |
| `tests/integration/test_end_to_end.py` | Milestone 2 |
| `tests/acceptance/test_events.py` | Milestone 3 |
| Your `ingestion.py`, `answering.py` and `api.py` | **Yours to extend** (Milestone 3) |

### Milestone 1: The logging setup (40 min)

Implement `JsonFormatter` and `configure_logging` in `logging_setup.py`; their docstrings are the specification.

```bash
uv run pytest tests/acceptance/test_logging_setup.py
uv run pytest          # Session 14 and 15 CLI tests pass again
```

- A `LogRecord`'s `extra=` fields are plain attributes on the record. `STANDARD_ATTRIBUTES` (provided) is how you tell them apart from the ones every record has (notebook Part 3).
- `datetime.fromtimestamp(record.created, UTC)` gives an aware time; `.isoformat(timespec="milliseconds")` formats it.
- `json.dumps(..., default=str)` writes values JSON can't represent (a `Path`, say) as text.
- "Replaces any handler this function added before": you need a way to recognise your own handler. An attribute on it, or a small subclass, both work.
- An exception is logged **by type only**. Before you move on, write down why: what can an exception's message contain?

### Milestone 2: Integration tests (30 min)

```bash
uv run pytest tests/integration
```

These tests ingest a copy of the documents through the CLI, ask through a fresh API, change the documents, and ask again. If one fails, your modules pass their own tests but disagree with each other, or with time. Work the loop from notebook Part 2: observe, write down hypotheses, inspect the cheapest one first.

Then:

1. In `ARCHITECTURE.md`, add a section **"Found by integration tests"**: each failure, its cause, and its fix. If nothing failed, say so, and name the integration test you think was most likely to catch a bug in your design, and why.
2. Write **one integration test of your own** in `tests/integration/`, for a behaviour that crosses modules and that no provided test covers. Some ideas: `status` after a file is deleted; the UI (with `AppTest`) and the API giving the same answer from one index; an evaluation run before and after a document changes.

### Milestone 3: Events (40 min)

Extend **your own** modules so they log these events, each as one record whose message and `event` field are the event's name, with the other fields passed in `extra=`. This table and the tests define them:

| Where | Event (message and `event` field) | Fields |
|---|---|---|
| `ingest()` | `ingest`, once per run, at INFO | `added`, `updated`, `unchanged`, `removed`, `failed` (counts), `chunks_written`, `duration_ms` |
| `answer_question()` | `answer`, once per answer (found or not), at INFO | `found`, `hits`, `sources`, `model`, `input_tokens`, `output_tokens`, `duration_ms` |
| `create_app()` | `request`, once per HTTP request, at INFO | `method`, `path`, `status`, `duration_ms` |

And in `create_app()`, give every request an ID:

- Use the caller's `X-Request-ID` header if it's 1 to 64 letters, digits or hyphens; otherwise generate one (`uuid.uuid4().hex`).
- Set it in `REQUEST_ID` while the request runs, so every line logged during the request carries it, and reset it afterwards.
- Return it in the `X-Request-ID` response header.

```bash
uv run pytest tests/acceptance/test_events.py
```

- FastAPI's `@app.middleware("http")` decorator wraps every request: `async def log_requests(request, call_next)`, then `response = await call_next(request)`.
- `ContextVar.set()` returns a token; `reset(token)` in a `finally` restores the previous value even when the request fails.
- `time.perf_counter()` is the right clock for durations; `time.time()` can jump.
- Finally, make `app_from_settings()` call `configure_logging(logging.INFO, json_format=True)`, so the service logs JSON when uvicorn runs it.

### Milestone 4: Observe (25 min)

Generate some logs, and answer questions from them:

```bash
ASSISTANT_GENERATOR=extractive uv run knowledge-assistant -v --log-format json evaluate 2> evaluation-logs.jsonl
```

In PowerShell: `$env:ASSISTANT_GENERATOR="extractive"; uv run knowledge-assistant -v --log-format json evaluate 2> evaluation-logs.jsonl`.

Write `scripts/log_report.py`, which reads a JSON Lines log file (skipping any line that isn't JSON: libraries sometimes print warnings) and prints, for the `answer` events: how many there were, the not-found rate, the p50 and p95 `duration_ms` (with `statistics.quantiles(..., method="inclusive")`), and the total tokens. Run it on your log file.

Then start the API (`uv run uvicorn --factory knowledge_assistant.api:app_from_settings`), send two requests with `curl` (one with `-H "X-Request-ID: demo-1"`), and find both of that request's lines in the output. (uvicorn's own access lines stay as plain text; that's fine.)

Add a section **"Operations"** to `ARCHITECTURE.md`: your report's output, the three alerts you'd set up first (notebook Part 4), and one question your logs **can't** answer yet.

### Milestone 5: Final documents (25 min)

- **`ARCHITECTURE.md`:** make it match the code. Put the known limitations in priority order, each with what you'd do about it.
- **`PRESENTATION.md`:** update it with anything the demonstration and its questions taught you.
- **`README.md`:** how to set up, ingest, ask, run the API and the UI, run the tests and the evaluation, as a new team member would need it.
- **Reflection** (below).

```bash
git tag session-16
```

---

## Acceptance criteria

- `uv run pytest` passes: the 72 Session 14 tests, the 64 Session 15 tests, the 22 Session 16 tests, and your own unit and integration tests.
- `uv run ruff check .` and `uv run ruff format --check .` are clean.
- `uv run knowledge-assistant --log-format json -v ask "..."` writes JSON lines, including an `answer` event, and no question text.
- The API returns an `X-Request-ID` header, and the request's lines in the log carry the same ID.
- `ARCHITECTURE.md`, `EVALUATION.md`, `PRESENTATION.md` and `README.md` are current, and the capstone meets the [rubric](../../../assessments/capstone-rubric.md).

## Testing

| Command | Expected |
|---|---|
| `uv run pytest tests/acceptance/test_logging_setup.py` | 9 passed (Milestone 1) |
| `uv run pytest tests/integration` | 7 passed, plus yours (Milestone 2) |
| `uv run pytest tests/acceptance/test_events.py` | 6 passed (Milestone 3) |
| `uv run pytest` | 158 passed, plus yours |

## Debugging guidance

| Symptom | Where to look |
|---|---|
| Session 14 and 15 CLI tests fail right after the copy | Expected until `configure_logging` exists (Milestone 1) |
| `TypeError: Object of type PosixPath is not JSON serializable` | `json.dumps`'s `default=` |
| JSON lines contain `args`, `pathname`, `lineno` ... | You dumped every attribute; compare with `STANDARD_ATTRIBUTES` |
| Every line appears twice | `configure_logging` added a second handler instead of replacing its own |
| `test_the_request_id_is_included_when_there_is_one` fails | Does `configure_logging` call `install_request_ids()`? |
| The `answer` event has no `request_id` in the API test | Did the middleware **set** `REQUEST_ID` before `call_next`, and reset it only afterwards? |
| An integration test fails, but every acceptance test passes | That's what integration tests are for: notebook Parts 1 and 2 |
| `uvicorn --factory` logs nothing from the assistant | `app_from_settings()` must call `configure_logging(...)`; without a handler, INFO records are dropped |

## Extension challenges (optional)

1. **Metrics.** Count answers, not-found answers and errors in memory, and expose them on `GET /metrics` as JSON. What do you lose when the process restarts, and how do real systems avoid that?
2. **Slow-request warnings.** Log the `request` event at WARNING instead of INFO when it takes longer than a configurable limit.
3. **Overlapping ingestion.** Two `ingest` runs at once can interleave their writes. Make a second run wait or refuse, with a lock file, and test it.
4. **Docker.** Write a `Dockerfile` that runs the API with uvicorn, with the index on a volume. Which settings must come from the environment?

## Reflection

Add to `ARCHITECTURE.md`, or a `REFLECTION.md`:

1. Which bug in the whole capstone taught you the most, and which kind of test caught it?
2. What can your logs tell an on-call engineer at 3 a.m., and what can't they?
3. Looking back at Session 01: which Python habit changed most in how you write code?
4. Where did an AI assistant help most in the capstone, and where did you have to overrule it?
5. What will you learn next, and which part of this course will you use first?

## Deliverables

Your `knowledge-assistant` repository, tagged `session-16`, with:

- `logging_setup.py`, and the events in your `ingestion.py`, `answering.py` and `api.py`.
- Your own integration test, and `scripts/log_report.py`.
- `ARCHITECTURE.md` (including "Found by integration tests" and "Operations"), `EVALUATION.md`, `PRESENTATION.md`, an updated `README.md`, and your reflection.

This completes **Milestone 4**. Together with the final assessment, it's the evidence for the readiness decision in [`assessments/python-readiness.md`](../../../assessments/python-readiness.md).
