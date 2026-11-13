# Session 15 Assignment: Capstone Application

**Type:** Milestone 1 is **Independent**: extend your design before you build. Milestones 2 to 6 are **AI-assisted**: you may use Claude Code, or an approved assistant, following the Session 13 workflow. Writing them yourself is just as valid.
**Estimated time:** 3 hours
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb), your Session 14 `knowledge-assistant` (tagged `session-14`), Session 09 (structured output) and Session 07 (FastAPI)
**Project:** **Project 04**, the capstone. This session adds answers, an API, a UI and an evaluation; Session 16 reviews and presents it.

---

## Business scenario

The index works: it stays in sync with the documentation every night. Now the on-call engineers want to use it. They want to type a question into a web page and get a short answer with the runbook it came from. The incident-management system wants to call the same thing over HTTP. And the team lead wants to know, before rolling it out, how often it finds the right document and how often it answers questions it shouldn't.

The non-negotiables, from the team lead: **every answer cites its sources, and those sources really exist; questions the documentation doesn't cover get "I can't find this", not a guess; and no question or answer is ever written to a log.**

## Learning objectives

By completing this assignment you will:

- **Implement** query → retrieve → build context → generate → cite, with "not found" at two levels.
- **Validate** a model's citations, and refuse answers that can't be traced to a source.
- **Expose** one service through FastAPI and a Streamlit UI, mapping each failure to the right status or message.
- **Evaluate** retrieval hit rate, answer rate, grounded rate and rejection rate on a synthetic question set, and **interpret** the misses.
- **Choose** a threshold from measurements without fooling yourself.

## Prerequisites

- Your `knowledge-assistant` from Session 14, with all 72 acceptance tests passing, tagged `session-14`, and a clean `git status`.
- An index built with the real embedder: `uv run knowledge-assistant ingest`.
- Optional: the OpenAI key from Session 09, for Milestone 6's live run. **Everything else, including all tests, runs without a key.**

> **Rules for AI-assisted milestones** are the same as last week: plan first, small steps, run the tests yourself, review every diff, and never let an assistant edit `tests/acceptance/` or `tests/conftest.py`.

---

## Project setup

Copy the Session 15 files over your project, then add the new dependencies:

```bash
# macOS / Linux / Git Bash
cp -r ~/python-ai-engineering-bridge/projects/04-rag-capstone/session-15/. ~/skillup/knowledge-assistant/

# PowerShell
Copy-Item -Recurse -Force ~\python-ai-engineering-bridge\projects\04-rag-capstone\session-15\* ~\skillup\knowledge-assistant\
```

```bash
cd ~/skillup/knowledge-assistant
git status                       # see exactly what the copy added and replaced
uv add "fastapi[standard]" openai streamlit
uv run pytest
```

The copy **replaces** four provided files: `errors.py`, `settings.py`, `cli.py` and `tests/conftest.py`. If you changed any of them last week, `git diff` shows your changes; merge them back by hand. Everything else it adds is new.

Your Session 14 tests still pass, and so do `test_generation.py` (it checks the provided generators) and one evaluation test that checks the question set. The other new tests fail or error until you've written the modules. Commit before you start: `git commit -am "Session 15 files"`.

| File | Status |
|---|---|
| `schemas.py` | Provided: `AskRequest`, `SourceRef`, `Answer`, the public contract. Read it first |
| `generation.py` | Provided: the `Generator` protocol, `OpenAIGenerator` (Responses API, structured output, errors translated as in Project 03), and `ExtractiveGenerator`, an offline stand-in that "answers" with source `[1]` |
| `prompts.py` | Provided: the instructions sent with every question |
| `assistant.py` | Provided: `Assistant`, which bundles store, embedder, generator and settings, and `build_assistant()` |
| `errors.py`, `settings.py`, `cli.py` | Provided, replaced: new errors, the generator and threshold settings, and the `ask` and `evaluate` commands |
| `.streamlit/config.toml` | Provided: no usage statistics, and the UI only on `localhost` |
| `data/eval/questions.jsonl` | 20 questions: 16 answerable, with their expected files, and 4 the documentation doesn't answer |
| `answering.py` | **Yours** (Milestone 2) |
| `api.py` | **Yours** (Milestone 3) |
| `ui.py` | **Yours** (Milestone 4) |
| `evaluation.py` | **Yours** (Milestone 5) |

New settings: `ASSISTANT_GENERATOR` (`openai` or `extractive`), `ASSISTANT_TOP_K` (default 4) and `ASSISTANT_MIN_SCORE` (default 0.6 for fastembed, 0.2 for the hashing embedder). The LLM uses Session 09's variables: `OPENAI_API_KEY`, `LLM_MODEL` and so on. Add the ones you use to `.env`; for this week's work without a key, set `ASSISTANT_GENERATOR=extractive`.

---

## Requirements

| # | Requirement | Where | Tests |
|---|---|---|---|
| R1 | Retrieve the top `k` chunks scoring at least `min_score`; reject a blank question | `retrieve` | `test_answering.py` |
| R2 | Number the hits as sources: `[n] (citation)` then the text, separated by blank lines | `build_context` | `test_answering.py` |
| R3 | Nothing retrieved: "not found", **without calling the model** | `answer_question` | `test_answering.py` |
| R4 | The model says `answerable: false`: "not found", reporting the model and its tokens | `answer_question` | `test_answering.py` |
| R5 | Cited sources are the `citations` list plus every `[n]` in the text. No citations, or a number that wasn't given: `InvalidAnswerError` | `answer_question` | `test_answering.py` |
| R6 | Return only the cited sources, each with its original number | `answer_question` | `test_answering.py` |
| R7 | Never log the question or the answer | `answer_question` | `test_answering.py` |
| R8 | `GET /health`; `POST /ask` returns an `Answer`; 422 / 503 / 502 / 500 as documented; short error details | `create_app` | `test_api.py` |
| R9 | A page with a "Question" input and an "Ask" button that shows the answer and its sources, "not found", or an error message, and builds the assistant once | `ui.py` | `test_ui.py` |
| R10 | Load the question set; measure the four rates per group; record generation errors per question and carry on | `evaluation.py` | `test_evaluation.py` |

`test_cli_answers.py` runs `ask` and `evaluate` through the provided CLI.

---

## Implementation milestones

### Milestone 1: Extend the design (15 min, Independent)

Read `schemas.py`, `generation.py`, `prompts.py` and `assistant.py`, and the stubs. Then add a section **"Answering"** to `ARCHITECTURE.md`:

1. The path of one question, from `POST /ask` to the JSON response, module by module.
2. Why the API, the UI and the CLI contain no answering logic. What would break, and how would you notice, if they did?
3. Your two levels of "not found", and what each one costs.
4. What you will log in `answer_question`, and what you won't.

### Milestone 2: Answering (45 min)

Implement `retrieve`, `build_context` and `answer_question`.

```bash
uv run pytest tests/acceptance/test_answering.py
```

- `retrieve` is Session 11's, on the new store. Remember the store returns hits best first.
- Notebook Part 3 is the specification for citations: cases A to E. Write the check as a small function of its own, and add unit tests for it in `tests/unit/`.
- `SourceRef` takes the hit's citation and score; the tests compare scores to about three decimal places.
- Use `ScriptedGenerator` (in `tests/conftest.py`) in your own tests: set `answer`, `citations`, `answerable` or `error`, and read `calls` afterwards.

### Milestone 3: The API (30 min)

Implement `create_app(assistant)`.

```bash
uv run pytest tests/acceptance/test_api.py
uv run uvicorn --factory knowledge_assistant.api:app_from_settings
```

Open `http://127.0.0.1:8000/docs`, and ask a question from the interactive page. The response schema shown there comes from `Answer`: that's why the route's return type matters.

- Pydantic validates `AskRequest` (length, blank questions) before your code runs; that's where the 422s come from.
- "Not found" is **200** with `found: false` (notebook Part 4).
- `--factory` tells uvicorn to call `app_from_settings()` to get the app, so the assistant (and the embedding model) is built at startup, not at import time. A missing key fails at startup, which is what you want for a service.

### Milestone 4: The UI (30 min)

Implement `ui.py`. Its docstring lists what the page must do.

```bash
uv run pytest tests/acceptance/test_ui.py
uv run streamlit run src/knowledge_assistant/ui.py
```

- Keep the page small: a title, the input, the button, the answer, and the sources under it. Notebook Part 5 explains the rerun model and `st.cache_resource`.
- Catch `AssistantError` and show `st.error(...)`: the tests check that a missing key and an index built with other settings each produce a message, not a traceback.
- Run it from the project folder, so Streamlit finds `.streamlit/config.toml`. Its first lines of output should show only a `localhost` URL.

### Milestone 5: Evaluation (30 min)

Implement `load_questions`, the three `QuestionResult` properties, the four rates and `evaluate`.

```bash
uv run pytest tests/acceptance/test_evaluation.py tests/acceptance/test_cli_answers.py
```

Quiz Q3 shows the mistake to avoid. Read each property's docstring twice: "of which questions" matters as much as "which ones count".

### Milestone 6: Measure and interpret (30 min)

Run the evaluation offline, with the real embedder:

```bash
ASSISTANT_GENERATOR=extractive uv run knowledge-assistant evaluate      # macOS / Linux / Git Bash
$env:ASSISTANT_GENERATOR="extractive"; uv run knowledge-assistant evaluate   # PowerShell
```

With the reference solution's chunking, this reported a 94% retrieval hit rate, 100% answer rate, 88% grounded rate and 75% rejection rate, with three questions listed. Your numbers may differ a little if you chunk differently. Then create `EVALUATION.md` and answer, with evidence from the output:

1. **Each listed question:** why did it go wrong? Use `uv run knowledge-assistant search "..." -k 6` to see what was retrieved, and with which scores. Is the cause retrieval, the threshold, or the generator?
2. **The extractive generator's grounded rate:** what is it really measuring? (Notebook Part 6.)
3. **The threshold, honestly.** Before looking at any scores, write **six new questions** in a file of your own: three the documentation answers, and three it doesn't but that sound as if it might. Then try `ASSISTANT_MIN_SCORE` at 0.6 and 0.65 on the original 20, and on your six. Which would you ship, and why? (Notebook Part 1, and quiz Q4.)
4. **Optional, with a key (paid):** set `ASSISTANT_GENERATOR=openai` and run `uv run knowledge-assistant ask "How do I promote the orders database replica?"` once, then the evaluation. Each question sends about 1,000–1,500 input tokens (the instructions plus four chunks) and gets about 100 back, so the 20 questions are roughly 25,000 input tokens: check your model's price before you run. Compare the grounded and rejection rates with the offline run. Did the model decline the vacation-days question?

Commit, and tag:

```bash
git tag session-15
```

---

## Acceptance criteria

- `uv run pytest` passes: the 72 Session 14 tests, the 64 Session 15 tests, and your own unit tests.
- `uv run ruff check .` and `uv run ruff format --check .` are clean.
- `POST /ask` and the Streamlit page both answer *"How do I promote the orders database replica?"* with `runbooks/database-failover.md` as a source, and say "not found" for *"What will the weather be in Zurich tomorrow?"*.
- `knowledge-assistant evaluate` runs offline, and `EVALUATION.md` explains every question it lists.
- No question or answer appears in any log output.

## Testing

| Command | Expected |
|---|---|
| `uv run pytest tests/acceptance/test_generation.py` | 10 passed, from the start (provided code) |
| `uv run pytest tests/acceptance/test_answering.py` | 18 passed (Milestone 2) |
| `uv run pytest tests/acceptance/test_api.py` | 13 passed (Milestone 3) |
| `uv run pytest tests/acceptance/test_ui.py` | 7 passed (Milestone 4) |
| `uv run pytest tests/acceptance/test_evaluation.py tests/acceptance/test_cli_answers.py` | 16 passed (Milestone 5) |
| `uv run pytest` | 136 passed, plus yours |

The suite runs in about 25 seconds. It never calls a real model: generators are scripted, and `OpenAIGenerator` is tested against a fake Responses API at the HTTP level, as in Project 03.

## Debugging guidance

| Symptom | Where to look |
|---|---|
| `test_generation.py` fails | Your setup, not your code: did `uv add` finish, and did the copy replace `errors.py` and `settings.py`? |
| `test_nothing_retrieved_means_not_found_without_calling_the_model` fails | Is the generator called before you check for hits? |
| `test_citations_in_the_text_count...` fails | You read only `citations`. Notebook Part 3, case D |
| `test_only_cited_sources_are_returned_with_their_original_numbers` fails | You renumbered the sources from 1 |
| The API returns 500 for an outage | Which exception did you catch, in which order? `GeneratorUnavailable` and `GeneratorConfigurationError` are both `GenerationError`s |
| `test_the_openapi_schema_documents_ask` fails | Give the route a return annotation (`-> Answer`) or `response_model=Answer` |
| UI test: `ValueError: not enough values to unpack` | No text input labelled exactly `Question`, or no button labelled exactly `Ask` |
| `test_the_assistant_is_built_once...` fails | `build_assistant()` runs on every rerun: notebook Part 5, quiz Q2 |
| The UI shows a traceback | An `AssistantError` escaped. Building the assistant can fail too, not only `ask` |
| Rejection rate rises during an outage | Quiz Q3 |
| `streamlit run` prints a Network URL | You ran it from another folder, so `.streamlit/config.toml` wasn't found |

## Extension challenges (optional)

1. **Show the evidence.** In the UI, put each source's chunk text in an `st.expander` under its citation, so the reader can check the answer without opening the file.
2. **Streaming.** Answers from a real model take a few seconds. Investigate streaming the text to the page (`st.write_stream`) while keeping the citation check. What has to change in the generator, and what can you only check at the end?
3. **A second model.** Write an `AnthropicGenerator` (Session 09's alternative provider) and compare the two on the evaluation. How much of `OpenAIGenerator` did you reuse?
4. **Fix the vocabulary gap.** The P2 question misses because the policy says "response targets", not "resolve". Try a fix (adding the title to each chunk differently, a synonym in the question, a different chunk size) and measure every rate before and after. Did anything else get worse?
5. **An evaluation report.** Make `evaluate` write a JSON report, and write a script that compares two reports question by question.

## Reflection

Answer in `EVALUATION.md` or `REFLECTION.md`:

1. Which of the four rates would you put on a dashboard for the team lead, and which would you check before every change? Why are they different?
2. Your assistant answered a question with a valid citation, and the answer was still wrong. How could that happen, and what would catch it?
3. What would you need to change before 300 engineers used this every night? Name the first three things.
4. If you used an assistant: which part of this week's code did you trust least, and how did you check it?

## Deliverables

Your `knowledge-assistant` repository, tagged `session-15`, containing:

- Your `answering.py`, `api.py`, `ui.py` and `evaluation.py`, and your unit tests.
- `ARCHITECTURE.md` with its new "Answering" section.
- `EVALUATION.md`: the offline evaluation output, your explanations, the threshold decision with your six new questions, and (optionally) the live comparison.

Session 16 starts from this tag: you'll present the whole assistant and defend its design.
