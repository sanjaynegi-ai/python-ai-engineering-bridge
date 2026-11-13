# Session 10 Assignment: Triage with LangChain, and an Honest Comparison

**Type:** Independent. Complete this without an AI coding assistant; Session 13 covers AI-assisted work.
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb), and your Session 09 work on Project 03
**Project:** **Project 03: LLM-Powered Application** (`incident-triage`), stage 2 of 3

---

## Business scenario

Your direct-SDK triage from Session 09 works. In the design review, two colleagues disagree:

- *"We should use LangChain. It's the standard, it lets us switch providers, and we'll need it for retrieval anyway."*
- *"It's another layer of dependencies we don't need for one API call. When it breaks, nobody will understand why."*

The team lead asks you to settle it with evidence: build the same triage with LangChain, behind the same `Triager` interface, prove that both versions behave identically, and write a short comparison that recommends one for this tool.

## Learning objectives

By completing this assignment you will:

- **Implement** a LangChain chain from a prompt template, a chat model and structured output.
- **Map** LangChain's exceptions, and the cases it doesn't cover, onto your application's errors.
- **Verify** behavioural equivalence of two implementations with the same contract tests.
- **Measure** and **compare** the two implementations on code size, dependencies, debuggability, testability and lock-in.
- **Recommend** one approach for a specific application, with reasons.

## Prerequisites

- **Your Session 09 project** (`incident-triage`, tagged `session-09`) with all 67 acceptance tests passing.
- The Session 10 concepts notebook.
- **Optional:** an OpenAI API key, for the live comparison in Milestone 4.

---

## Project setup

Before adding anything, record how many packages your environment has, for the comparison:

```bash
cd ~/skillup/incident-triage
uv pip list | wc -l              # PowerShell: (uv pip list | Measure-Object -Line).Lines
```

Then copy the contents of the course repository's `projects/03-llm-application/session-10/` over your project, and add the LangChain packages:

```bash
# macOS / Linux / Git Bash
cp -r ~/python-ai-engineering-bridge/projects/03-llm-application/session-10/. ~/skillup/incident-triage/

# PowerShell
Copy-Item -Recurse -Force ~\python-ai-engineering-bridge\projects\03-llm-application\session-10\* ~\skillup\incident-triage\
```

```bash
uv add langchain-core langchain-openai
git add .
git commit -m "Session 10 starter files"
git tag session-10-start
uv run pytest
```

| File | Status |
|---|---|
| `src/incident_triage/langchain_triager.py` | Stub. Yours |
| `src/incident_triage/cli.py` | Updated, provided: a new `--engine direct\|langchain\|offline` option (`--offline` still works) |
| `tests/acceptance/test_langchain.py` | Provided. Don't edit |

pytest stops with **1 collection error**: `test_langchain.py` imports `PROMPT`, which doesn't exist yet. Your Session 09 tests still pass:

```bash
uv run pytest tests/acceptance --ignore=tests/acceptance/test_langchain.py
```

Read `test_langchain.py` before you start. Most of its tests are a **contract**: they run twice, once against your `OpenAITriager` and once against `LangChainTriager`, with the same fake API and the same expectations.

---

## Requirements

| # | Requirement |
|---|---|
| R1 | All 119 acceptance tests pass, unchanged: Session 09's 67 and the 52 in `test_langchain.py`. |
| R2 | `LangChainTriager` satisfies the `Triager` protocol, and raises only the package's own exceptions for every failure the contract tests cover. |
| R3 | The report is sent as its own human message; `TRIAGE_INSTRUCTIONS` is the system message. |
| R4 | Retries happen in one place only: the SDK's, configured from `llm_max_retries`. No `with_retry`. |
| R5 | Only public imports: `langchain_core.*`, `langchain_openai`, `openai`. Nothing from a module whose path is internal, such as `langchain_openai.chat_models.base`. |
| R6 | `COMPARISON.md` with the measurements and a recommendation (Milestone 4). |
| R7 | At least **6** test cases of your own in `tests/unit/`. |
| R8 | `uv run ruff check .` and `uv run ruff format --check .` pass. |

---

## Implementation milestones

### Milestone 1: Predict

Reread your `llm.py`. In `NOTES.md`, predict:

1. Which parts of `OpenAITriager` LangChain will do for you, and which you'll still write.
2. Roughly how many lines `LangChainTriager` will need, compared with `OpenAITriager`.
3. One way the two versions might behave **differently** for the same API response.

### Milestone 2: The prompt

Define `PROMPT`, a `ChatPromptTemplate` with two messages: `TRIAGE_INSTRUCTIONS` as the system message, and the report as the human message, through one variable, `{report}`.

```bash
uv run pytest tests/acceptance/test_langchain.py -k prompt
```

### Milestone 3: `LangChainTriager`

Implement it following the stub's docstrings:

- **`__init__(model)`** keeps the model, and builds `self.chain` as `PROMPT` piped into the model's structured output (`TriageResult`, `include_raw=True`).
- **`from_settings(settings, *, http_client=None)`** builds a `ChatOpenAI` with the same configuration as `OpenAITriager.from_settings`: model, key, base URL, timeout, retries, output token limit, OpenAI's Responses API, and the `http_client` (the tests use it). No key: `LLMConfigurationError`, before any request.
- **`triage(report)`** has the **same contract** as `OpenAITriager.triage`, including the same error table as Session 09.

Design hints, not a recipe:

- `langchain_core.exceptions` has provider-neutral classes (`ModelAuthenticationError`, `ModelRateLimitError` ...). Use them where you can. The concepts notebook (Part 6) shows which statuses they **don't** cover.
- With `include_raw=True`, look at all three keys of the result. A refusal and invalid output surface differently (Part 5).
- Token usage and the model name are on the raw `AIMessage`: `usage_metadata` and `response_metadata`.
- Read failing test names carefully: when a contract test fails only for `langchain`, the difference is in your mapping; when it fails for both, look at the test's setup.

```bash
uv run pytest tests/acceptance/test_langchain.py
uv run pytest
```

### Milestone 4: Compare

Write `COMPARISON.md` with these measurements, and a recommendation.

1. **Code size.** Count the non-blank, non-comment lines in `llm.py` and `langchain_triager.py`:

   ```bash
   uv run python -c "import sys; [print(f, sum(1 for l in open(f, encoding='utf-8') if l.strip() and not l.strip().startswith('#'))) for f in sys.argv[1:]]" src/incident_triage/llm.py src/incident_triage/langchain_triager.py
   ```

2. **Dependencies.** Run `uv pip list | wc -l` again, and compare with the number you recorded before setup. Which packages arrived, and who maintains them?
3. **Debuggability.** Make one acceptance test fail on purpose in each implementation (for example, return `LLMUnavailable` for a 401), run it with `uv run pytest -x --tb=long`, and compare the tracebacks. How many frames are your code, and how many are library code? Which was quicker to understand? Undo the change.
4. **Testability.** Which tests could you reuse unchanged? What did you have to learn to test the LangChain version?
5. **Behaviour.** List every difference you found between the two, such as how the instructions are sent, how errors arrive, or what `include_raw` does and doesn't catch.
6. **Lock-in and change.** What would switching to Anthropic involve in each version?

**Optional, with an API key:** run both engines on the sample reports, and compare the triage and the token usage:

```bash
uv run incident-triage data/reports.jsonl --engine direct --out out/direct.json
uv run incident-triage data/reports.jsonl --engine langchain --out out/langchain.json
```

End with **one paragraph of recommendation** for this tool, as you'd present it in the design review. Either answer can be right; the reasons are what's assessed.

### Milestone 5: Your own tests

Create at least **6** test cases in `tests/unit/`. Ideas:

- `PROMPT` escapes literal braces: a report containing `{"json": true}` reaches the model unchanged;
- the chain works with `LangChainTriager(model)` given a model built by hand;
- `chain.batch([...], config={"max_concurrency": 2})` against `fake_openai` returns results in order;
- an `AIMessage` without `usage_metadata` gives zero tokens;
- `triage_all` with `LangChainTriager` records a refusal and continues;
- the CLI with `--engine langchain` and a reports file with one report.

Prove that two of your tests can fail, as before.

### Milestone 6: Quality gate

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
git add .
git commit -m "Session 10: LangChain triage and comparison"
git tag session-10
```

---

## Acceptance criteria

| Check | Expected result |
|---|---|
| `uv run pytest tests/acceptance` | `119 passed`, with no API key and no network |
| `uv run pytest tests/unit` | Your earlier tests plus at least 6 new ones pass |
| `git grep -n -E "chat_models\.base\|with_retry" -- src` | No output: no internal imports, no extra retries |
| `uv run incident-triage data/reports.jsonl --engine langchain` without a key | A one-line error naming `OPENAI_API_KEY`; exit code `2` |
| `git diff session-10-start -- tests/acceptance tests/conftest.py` | No output |
| `uv run ruff check .` and `uv run ruff format --check .` | Both pass |
| `COMPARISON.md` | All six measurements and a recommendation |
| `NOTES.md` | Milestone 1 predictions, checked against the results, and the reflection |

## Debugging guidance

| You see | Where to look |
|---|---|
| `ImportError: cannot import name 'PROMPT'` | Milestone 2: `PROMPT` must be assigned, not only annotated. |
| `KeyError: ... missing variables` | The template's variable must be `{report}`, and `triage` must pass `{"report": report.text}`. |
| Contract tests fail only for `[langchain]` with `ValidationError` | It escapes from the chain even with `include_raw=True`: catch it. |
| Contract tests for `408` and `409` fail only for `[langchain]` | LangChain doesn't map them: they arrive as `openai.APIStatusError` subclasses. |
| `test_refusal[langchain]` gets `LLMInvalidOutput` | A refusal leaves `parsed` as `None` and sets `parsing_error`; the text is in a `refusal` block of `raw.content`. |
| `test_retries_come_from_the_sdk[langchain]` sees more than 3 requests | Something retries on top of the SDK. |
| `test_settings_are_used[langchain]` fails on `max_output_tokens` | `ChatOpenAI`'s parameter is `max_tokens`. With the Responses API it's sent as `max_output_tokens`. |
| Requests go to `/chat/completions` | `use_responses_api=True` is missing. |
| A real network call, or a hang, in tests | `http_client` isn't passed to `ChatOpenAI`. |
| `test_model_name_comes_from_the_reply[langchain]` fails | Use `raw.response_metadata["model_name"]`, not the configured model. |

## Extension challenges (optional)

1. **Concurrent batch.** Add `LangChainTriager.triage_many(reports, max_concurrency=4)` using `self.chain.batch(..., return_exceptions=True)`, mapping each exception as `triage` does. Test that results stay in order and that one failure doesn't lose the others. Compare it with Session 08's approach.
2. **A visible fallback.** Wrap the chain with `with_fallbacks` to the `KeywordTriager` for provider outages only, and record in `Triage.model` which engine answered. Write tests for both paths, and for a `ValidationError` **not** falling back.
3. **Anthropic.** Add `--engine anthropic` with `ChatAnthropic` (`uv add langchain-anthropic`) and `method="json_schema"`. How much of `LangChainTriager` did you reuse? Fake it in tests with a local HTTP server, as the concepts notebook does.
4. **Token logging.** Write a callback handler that logs token usage per request with `logging`, and attach it with `with_config(callbacks=...)`. Check that it never logs report text.

## Reflection

Answer briefly in `NOTES.md`:

1. How close were your Milestone 1 predictions?
2. Which behaviour difference between the two versions would have caused a production bug if the contract tests hadn't caught it?
3. When will this project's decision need revisiting? What would change your recommendation?
4. How does LangChain compare with frameworks you know (Spring, ASP.NET, Express middleware) in how much it hides?

## Deliverables

Submit **one** of the following, as your course instructions specify:

- a link to a Git repository containing the project, with the `session-10` tag (push only to a repository you own; keep it private if you prefer), **or**
- a `.zip` of the project folder **without** `.venv/`, `out/` and `.env`.

The submission must include:

- [ ] `PROMPT` and `LangChainTriager` implemented
- [ ] `tests/acceptance/` and `tests/conftest.py` unchanged, and your `tests/unit/` with at least 6 new test cases
- [ ] `COMPARISON.md` with the measurements and your recommendation
- [ ] `NOTES.md` with your predictions and the reflection
- [ ] All acceptance criteria passing

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
