# Session 09 Assignment: Project 03 Begins, LLM-Assisted Triage

**Type:** Independent. Complete this without an AI coding assistant; Session 13 covers AI-assisted work.
**Estimated time:** 2.5–3 hours
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb); Sessions 05 (HTTP clients and errors), 06 (Pydantic) and 08 (partial failure)
**Project:** this starts **Project 03: LLM-Powered Application** (`incident-triage`), which grows in Sessions 10 and 12.

From this session on, the workbooks give you **requirements and acceptance criteria**, not step-by-step instructions. Design decisions are yours, within the requirements.

---

## Business scenario

Incident reports reach the Orbital Logistics (fictional) on-call team as free text, by email and chat. Today a person reads each one and sets a priority, an owning team and a category, and writes a one-line summary. The team lead wants a tool that does a first pass automatically, so that people check triage rather than write it.

The tool must:

- produce **structured, validated** triage, never free text pasted into a ticket;
- **keep going** when one report can't be triaged, and say why;
- **stop** at once when the configuration is wrong, instead of failing 500 times;
- show what a run **cost**;
- be **testable without an API key** and without spending anything;
- treat report text as **data**: some reporters will, deliberately or not, write things that look like instructions.

## Learning objectives

By completing this assignment you will:

- **Design** an output contract for an LLM as a Pydantic model, with business rules as validators.
- **Implement** a direct integration with OpenAI's Responses API: configuration, timeouts, retries, structured output.
- **Map** SDK exceptions and bad outputs to your own error types, deciding which are temporary, which are configuration problems, and which concern one report.
- **Record** token usage and calculate cost.
- **Test** LLM code at two levels, with a scripted triager and with an HTTP-level fake, and **explain** what each level proves.
- **Compare** LLM triage with a keyword baseline on difficult reports.

## Prerequisites

- The Session 09 concepts notebook.
- **Optional:** an OpenAI API key in `.env`, for Milestone 5's live run. Everything else, including every test, works without one.

---

## Project setup

```bash
# macOS / Linux / Git Bash
cp -r ~/python-ai-engineering-bridge/projects/03-llm-application/starter ~/skillup/incident-triage

# PowerShell
Copy-Item -Recurse ~\python-ai-engineering-bridge\projects\03-llm-application\starter ~\skillup\incident-triage
```

```bash
cd ~/skillup/incident-triage
git init
git add .
git commit -m "Project 03 starter"
git tag starter
uv sync
uv run pytest
```

Most tests fail, as expected. A few pass already, including the three in `test_fake_api.py`, which check the test fake itself, not your code.

| File | Status |
|---|---|
| `models.py` | `IncidentReport`, `Triage`, `TriageOutcome`, `TriageRun` and the literals provided; `TriageResult` and `Usage` are placeholders for you (Milestone 2) |
| `settings.py` | Yours (Milestone 2) |
| `llm.py` | The `Triager` protocol and `OpenAITriager.__init__` provided; `from_settings` and `triage` yours (Milestone 3) |
| `service.py` | `triage_all` yours (Milestone 4) |
| `prompts.py`, `errors.py`, `offline.py`, `loading.py`, `cli.py` | Provided. Read them |
| `tests/conftest.py`, `tests/acceptance/` | Provided; don't edit |
| `data/reports.jsonl` | 12 synthetic reports, including a prompt-injection attempt and a report in French |

---

## Requirements

| # | Requirement |
|---|---|
| R1 | All 67 acceptance tests pass, unchanged. |
| R2 | No test makes a network call. `uv run pytest` passes with no API key and no internet connection. |
| R3 | Only `llm.py` imports `openai`. Everything else depends on the `Triager` protocol and the package's own exceptions. |
| R4 | The API key is a `SecretStr`, and never appears in output, logs, exceptions or `repr`, not even partially. |
| R5 | Report text is sent only as the request's `input`, never inside `instructions`. |
| R6 | Every request has a timeout and an output token limit from settings; the SDK's own retries are configured from settings, and you add no retry loop of your own. |
| R7 | At least **8** test cases of your own in `tests/unit/`, at least 3 of them using `fake_openai`. |
| R8 | `uv run ruff check .` and `uv run ruff format --check .` pass. |

---

## Implementation milestones

### Milestone 1: Explore (15 min)

The command doesn't run yet: it needs the models, settings and batch service you write in Milestones 2 to 4. So start by reading.

1. Read `data/reports.jsonl`, then `offline.py`: the keyword rules of the `--offline` baseline.
2. Read `prompts.py`, `errors.py` and `cli.py`, then `FakeOpenAI` in `tests/conftest.py`.
3. In `NOTES.md`: predict how the keyword rules will triage `RPT-1009`, `RPT-1010` and `RPT-1011`, and what a good triage of each would be. You'll check your predictions in Milestone 5.

### Milestone 2: The contracts (25 min)

**`TriageResult`**, frozen:

| Field | Type | Rules |
|---|---|---|
| `priority` | `Priority` | |
| `team` | `Team` | |
| `category` | `Category` | |
| `affected_system` | `str` or `None` | **required** (no default); blank becomes `None`; stored stripped |
| `summary` | `str` | stored stripped; not blank; at most 160 characters |
| `tags` | `list[str]` | stored lower-case, stripped, without blanks or duplicates, sorted; at most 5 |

Give the fields a `Field(description=...)` where it helps the model: descriptions are part of the schema it sees.

**`Usage`**, frozen: `input_tokens` and `output_tokens` (`int`, 0 or more), and `cost_usd(*, input_per_million, output_per_million) -> float`.

**`Settings`**, read from the course's variable names (`LLM_MODEL`, `OPENAI_API_KEY` ...) and `.env`:

| Field | Type | Default |
|---|---|---|
| `llm_model` | `str` | `"gpt-5.6-terra"` |
| `openai_api_key` | `SecretStr \| None` | `None` |
| `openai_base_url` | `str \| None` | `None` |
| `llm_timeout_seconds` | positive float | `30.0` |
| `llm_max_retries` | `int` | `2` |
| `llm_max_output_tokens` | positive int | `2000` |
| `llm_input_usd_per_million`, `llm_output_usd_per_million` | `float \| None` | `None` |

```bash
uv run pytest tests/acceptance/test_models.py tests/acceptance/test_settings.py
```

### Milestone 3: `OpenAITriager` (60 min)

**`from_settings(settings, *, http_client=None)`** builds an `OpenAI` client from the settings: key, base URL, timeout and max retries, and passes `http_client` through (the tests use it to replace the network). Without a key, raise `LLMConfigurationError` mentioning `OPENAI_API_KEY`, before any request.

**`triage(report)`** sends **one** Responses API request with structured output (`responses.parse`, `text_format=TriageResult`), using `TRIAGE_INSTRUCTIONS` from `prompts.py` as the instructions and the report's text as the input. It returns a `Triage` with the parsed result, the model name **from the response**, and the usage.

Every failure becomes one of the package's exceptions:

| Situation | Raise |
|---|---|
| 401 or 403 | `LLMConfigurationError`, **without** the provider's message (it can contain part of the key) |
| 404 (an unknown model), 400, any other 4xx not listed here | `LLMConfigurationError` |
| Timeouts, connection errors, 429, 5xx, and 408/409, after the SDK's retries | `LLMUnavailable` |
| A refusal | `LLMRefusal`, including the model's explanation |
| Invalid or truncated JSON; output that breaks the contract | `LLMInvalidOutput`, naming the field(s) at fault |
| No parsed output and no refusal | `LLMInvalidOutput` |

Design hints, not a recipe:

- The SDK's exception classes are in the `openai` module: `openai.AuthenticationError`, `openai.APIConnectionError` and so on. Several share base classes, so the **order** of your `except` clauses matters. Check the hierarchy in Part 2 of the concepts notebook, or with `openai.APITimeoutError.__mro__`.
- A refusal doesn't raise: look for a content part of type `"refusal"` in `response.output` when `output_parsed` is `None`.
- `pydantic.ValidationError` carries the field names you need for the message (Session 06).
- Use `raise ... from error`, so the original exception is still in the traceback when you debug.

```bash
uv run pytest tests/acceptance/test_llm.py
```

28 tests. Read the test names first: they're the specification. Then work through them a group at a time: the request, the result, the failures, the configuration.

### Milestone 4: The batch (20 min)

Implement `triage_all(triager, reports, *, input_usd_per_million=None, output_usd_per_million=None)`, following its docstring: one `TriageOutcome` per report, in order; a `TriageError` for one report is recorded and the run continues; `LLMConfigurationError` stops the run; any other exception propagates. Total the tokens of the successful triages. The cost is `None` unless **both** prices are set.

```bash
uv run pytest tests/acceptance/test_service.py
uv run pytest
```

The service tests use a `ScriptedTriager`, not the OpenAI SDK: `triage_all` depends only on the protocol. In `NOTES.md`, explain what the service tests prove that the `fake_openai` tests don't, and the other way round.

### Milestone 5: Run it (15 min)

First the offline baseline, which needs no key:

```bash
uv run incident-triage data/reports.jsonl --offline
```

Open `out/triage.json`, and check your Milestone 1 predictions for `RPT-1009`, `RPT-1010` and `RPT-1011`.

**With an API key** (optional): copy `.env.example` to `.env`, set `OPENAI_API_KEY`, and set the two price variables to your model's prices from the provider's pricing page. Then:

```bash
uv run incident-triage data/reports.jsonl --out out/llm.json
```

Twelve short requests cost a small fraction of a US dollar with a small model; check the summary line. In `NOTES.md`, compare the LLM's triage with the baseline for `RPT-1009` (French), `RPT-1010` (an injection attempt) and `RPT-1011` (phishing). Did the LLM follow the injected instruction? Did it refuse anything? Run it a second time: are the results identical?

**Without a key**, set `OPENAI_API_KEY=not-a-real-key` for one run and record what happens, then remove it. Then answer the same comparison questions from what you expect, and come back to them if you get access to a key later.

### Milestone 6: Your own tests (20 min)

Create `tests/unit/` with at least **8** test cases, at least 3 using `fake_openai`. Ideas:

- a reply with `"usage": null`;
- a reply whose model name differs from the requested one (providers report the exact model version);
- a refusal containing a non-ASCII character;
- the CLI on a reports file with one blank line;
- `triage_all` with a generator instead of a list;
- an `AuthenticationError` whose message includes something that looks like a key: prove it never reaches your exception;
- the same report twice in one run.

As before, prove that two of your tests can fail, and record the failures in `NOTES.md`.

### Milestone 7: Quality gate (5 min)

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
git add .
git commit -m "Session 09: direct LLM triage"
git tag session-09
```

---

## Acceptance criteria

| Check | Expected result |
|---|---|
| `uv run pytest tests/acceptance` | `67 passed`, with no API key set and no network |
| `uv run pytest tests/unit` | At least 8 passed |
| `git grep -l -E "^(import openai\|from openai)" -- src` | Only `src/incident_triage/llm.py` |
| `uv run incident-triage data/reports.jsonl --offline` | 12 triaged; exit code `0` |
| `uv run incident-triage data/reports.jsonl` without a key | A one-line error naming `OPENAI_API_KEY`; exit code `2`; no traceback |
| `git diff starter -- tests` | No output |
| `uv run ruff check .` and `uv run ruff format --check .` | Both pass |
| `NOTES.md` | Milestones 1, 4, 5 and 6, and the reflection |

## Debugging guidance

| You see | Where to look |
|---|---|
| `openai.OpenAIError: Missing credentials` | You built `OpenAI()` without `api_key=`, and no environment variable is set. Pass the key from settings. |
| A real network error, or a test that hangs | `http_client` isn't passed to `OpenAI(...)`, so the real network is used. |
| `ModuleNotFoundError: No module named 'httpx'` | The OpenAI SDK is built on `httpx2`, Session 05's `httpx` successor. Import and type-hint `httpx2`. |
| `test_temporary_problems` gets `LLMConfigurationError` | A broad `except openai.APIStatusError` before the specific ones, or 408/409 not treated as temporary. |
| `test_configuration_problems` fails on `"not-a-"` | Your message includes the provider's error text. Write your own message. |
| `AttributeError: 'NoneType' object has no attribute ...` | A refusal: `output_parsed` is `None`. |
| A `pydantic.ValidationError` escapes from `triage` | Catch it and raise `LLMInvalidOutput`, with the field names. |
| `test_request_keeps_instructions_and_report_apart` fails | The report text is in the instructions. |
| Model output passes validation with a 300-character summary | The rule is missing from `TriageResult`, or the validator doesn't raise `ValueError`. |
| `test_json_schema_lists_every_field_as_required` fails | `affected_system` has a default. Remove it: required, but nullable. |
| A live run fails with `404` | The model name in `LLM_MODEL`, or your key can't use that model. |
| A live run fails with `429` at once | Rate limits, or no credit on the account: check the provider's dashboard. |

## Extension challenges (optional)

1. **`AnthropicTriager`.** Implement the same protocol with the `anthropic` SDK (`messages.parse(..., output_format=TriageResult)`, as in Part 8 of the notebook), selected by `LLM_PROVIDER=anthropic`. Fake it in tests with `httpx2.MockTransport`, and check your fake against `anthropic.types.Message`. How many lines outside the new class did you have to change?
2. **One retry for invalid output.** When the output breaks the contract, retry **once**, adding the validation error to the input so the model can correct itself. Record both requests' usage. When is this worth the cost?
3. **Concurrency.** Write `async` versions of the triager (`AsyncOpenAI`) and of `triage_all`, with a semaphore limiting concurrent requests (Session 08). Measure against the live API.
4. **A cheap secret check.** Before sending a report, reject it if it appears to contain a password or API key (a few regular expressions), with its own error type. Why must this happen **before** the LLM call?
5. **Plug into Project 02.** Write a function that turns a `Triage` into a ticket record accepted by Project 02's `POST /tickets`. Which fields are missing, and where would they come from?

## Reflection

Answer briefly in `NOTES.md`:

1. Which failure cases would you have missed without the error table? Which do you expect to see most often in production?
2. What does `fake_openai` prove about your code, and what can't it prove?
3. Where would you put a person in the loop for this tool, and why?
4. Compare calling an LLM with calling the Asset Inventory in Session 05. What's the same, and what's genuinely new?

## Deliverables

Submit **one** of the following, as your course instructions specify:

- a link to a Git repository containing the project, with the `session-09` tag (push only to a repository you own; keep it private if you prefer), **or**
- a `.zip` of the project folder **without** `.venv/`, `out/` and `.env`.

Never include `.env` or an API key in a submission.

The submission must include:

- [ ] `TriageResult`, `Usage`, `Settings`, `OpenAITriager` and `triage_all` implemented
- [ ] `tests/` unchanged except for your new `tests/unit/` with at least 8 test cases
- [ ] `NOTES.md` with your milestone answers, the comparison and the reflection
- [ ] All acceptance criteria passing
