# Session 13 Assignment: Build with an Assistant, Review an Assistant

**Type:** Part A is **AI-assisted**: use Claude Code. Part B is **AI-review**: review code an assistant wrote, by hand first, then with Claude Code.
**Estimated time:** 3–3.5 hours
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb), and your Project 03 (`incident-triage`, tagged `session-12`)
**Project:** **Project 03** again, on its own branch and tags. Project 03 itself was completed in Session 12.

---

## Business scenario

**Part A.** The on-call team has started using `--route` in production. Two weeks in, an engineer was paged at 3 a.m. for an incident she thinks was a P3, and nobody can tell why it was routed to her: the results file was overwritten the next morning. The team lead asks for an **audit log**: one line per routing decision, appended forever, that answers "why was this paged?", without storing report text, which can contain customer and employee details.

**Part B.** A colleague used an AI assistant to add **duplicate detection**, so that five reports of the same outage page once, not five times. The pull request description says all tests pass. You're the reviewer.

## Learning objectives

By completing this assignment you will:

- **Configure** Claude Code for a project with a `CLAUDE.md`, and choose its permission mode deliberately.
- **Explore** an unfamiliar codebase with an assistant, and **verify** its summary against the code.
- **Write** an implementation request with requirements, constraints, acceptance criteria and a check the assistant can run.
- **Implement** a feature through Understand → Plan → Implement → Test → Review → Explain.
- **Review** AI-generated code for correctness, invented and outdated APIs, privacy, error handling, weak tests and needless abstraction, with evidence.
- **Compare** your review with an assistant's, and **recognise** text that tries to steer an assistant.

## Prerequisites

- **Claude Code**, installed and signed in: see [`docs/using-claude-code.md`](../../../docs/using-claude-code.md). It needs a Pro, Max, Team, Enterprise or Console account; the free plan doesn't include it. If your employer approves a different assistant, you may use it instead: the workflow is the same, and you'll adapt the command names.
- **Your Project 03**, tagged `session-12`, with all 171 acceptance tests passing, committed with a clean `git status`.
- The Session 13 concepts notebook.
- **No LLM API key** is needed for the project's tests. Claude Code's own usage counts against your Claude plan or API billing: check it with `/usage`.

> **Rules for this assignment.** Don't paste secrets or `.env` contents into the assistant. Read every command before you approve it. You're responsible for every line you submit, and you'll be asked to explain it.

---

## Project setup

```bash
cd ~/skillup/incident-triage
git status                       # must be clean
git switch -c session-13-audit
```

Copy the new acceptance tests from the course repository's `projects/03-llm-application/session-13/tests/` into your project. Don't copy the `review/` folder yet: Part B uses it.

```bash
# macOS / Linux / Git Bash
cp -r ~/python-ai-engineering-bridge/projects/03-llm-application/session-13/tests/. tests/

# PowerShell
Copy-Item -Recurse -Force ~\python-ai-engineering-bridge\projects\03-llm-application\session-13\tests\* tests\
```

```bash
git add tests
git commit -m "Session 13: audit acceptance tests"
git tag session-13-start
uv run pytest
```

`tests/acceptance/test_audit.py` fails to import: `incident_triage.audit` doesn't exist yet. Your other 171 acceptance tests still pass:

```bash
uv run pytest tests/acceptance --ignore=tests/acceptance/test_audit.py
```

---

# Part A: The audit log (AI-assisted)

## Requirements

The feature, as the team lead specified it. The acceptance tests are the definitive version: read them.

| # | Requirement |
|---|---|
| A1 | A new module `incident_triage/audit.py` with a Pydantic model `AuditRecord`, a function `audit_records(run, *, at)` and a function `append_audit(path, records)`. |
| A2 | `AuditRecord` has exactly these fields: `timestamp` (timezone-aware, in UTC), `report_id`; `action`, `team` and `reasons` from the routing's dispatch (so `team` is `None` for a review); `path`, `attempts`, `model` (the triager that produced the triage, or `None`), `llm_error` (whether the LLM failed at least once), `input_tokens`, `output_tokens` (0 without a triage). |
| A3 | `audit_records(run, *, at)` returns one record per routing, in order, stamped with `at` converted to UTC, and raises `ValueError` if `at` has no time zone. |
| A4 | **No report text, summaries, error messages or model output** in a record. A refusal is recorded with the single reason `"the model refused"`. |
| A5 | `append_audit(path, records)` appends one JSON object per line (UTF-8), creating the file and its folder if needed, never changes existing lines, and returns the number of records written. |
| A6 | The CLI gains `--audit PATH`. With `--route`, it appends the run's records stamped with the current UTC time and prints `Audit: N records appended to PATH`. Without `--route`, it prints `error: --audit requires --route` to stderr and exits `2`, writing nothing. If the log can't be written, it prints an error (no traceback) and exits `2`; the results file is still written. |
| A7 | All 188 acceptance tests pass, **unchanged**: the 171 earlier ones and the 17 in `test_audit.py`. |
| A8 | At least **5** test cases of your own in `tests/unit/`, at least two of which you've shown can fail. |
| A9 | `uv run ruff check .` and `uv run ruff format --check .` pass. |

## Milestones

### Milestone A1: Set up Claude Code for the project (15 min)

1. Start Claude Code in the project folder (`claude`), in **plan mode** (`Shift+Tab` until the status bar shows plan mode, or `claude --permission-mode plan`).
2. Run `/init` to draft a `CLAUDE.md`. Then **edit it yourself** until it's short and correct. It should contain what the assistant can't guess: how to run the tests and Ruff (`uv run ...`), that `tests/acceptance/` and `tests/conftest.py` must never be changed, that no test may call a real API, that data is synthetic and must stay so, and where the main modules are. Delete anything it could learn by reading the code.
3. Run `/context` and check that `CLAUDE.md` is loaded.
4. Commit `CLAUDE.md`.

In `NOTES.md`, record what `/init` produced that you **removed**, and why.

### Milestone A2: Understand (15 min)

Still in plan mode, ask Claude Code to explain:

- how a report flows from the CLI through routing to the results file;
- what `tests/acceptance/test_audit.py` requires, in a list.

Write its answers into `NOTES.md` in your own words, then **verify three of its claims** against the code yourself (open the file, find the line). Record each claim, where you checked it, and whether it was right. If anything was wrong or vague, note how you'd have caught it.

### Milestone A3: Plan (15 min)

Write your implementation request in `NOTES.md` first, using the structure from the concepts notebook (Part 2): goal, context, constraints, acceptance criteria, verification, out of scope. Then give it to Claude Code, still in plan mode, and ask for a plan.

Review the plan before approving it. Does it change only what it should? Does it say how it will meet requirement A4? Does it plan to touch the tests? Edit the plan if needed (`Ctrl+G` opens it in your editor). Record the plan, and what you changed, in `NOTES.md`.

### Milestone A4: Implement and test (40 min)

Switch to **Manual mode** and approve the plan. Work in small steps: approve each edit and command only after reading it. After each step:

```bash
uv run pytest
git diff --stat
```

Commit when a step works. Ask Claude Code to add your **own** tests (A8) too, then check them: do they test the requirements, or only that the code runs?

If something goes wrong twice, stop: `/clear` (or `/rewind`), understand the failure yourself, and write a better request (concepts notebook, Part 1).

### Milestone A5: Review (25 min)

Review the complete change as you would a colleague's pull request:

```bash
git diff session-13-start
```

1. **Your review first.** Go through the checklist from the concepts notebook's review diagram, line by line. Record every finding in `NOTES.md`.
2. **Then a fresh review:** run `/code-review` in Claude Code. Compare its findings with yours: what did it find that you missed, what did you find that it missed, and which of its findings are wrong or irrelevant?
3. **Prove two of your unit tests can fail:** break the code they cover, run them, record the failure, restore the code.
4. Fix what needs fixing, and run the quality gate:

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
git diff session-13-start -- tests/acceptance tests/conftest.py   # must print nothing
```

### Milestone A6: Explain (15 min)

In `NOTES.md`, without asking the assistant, answer:

1. Why does the audit store `llm_error` as a boolean instead of the error message?
2. Why is a refusal recorded as "the model refused", without the model's words?
3. Why must the time be timezone-aware, and stored in UTC?
4. Pick the line of your implementation you understand least. Explain it now, using the documentation if needed.
5. What did the session cost (`/usage`), and roughly how much time did the assistant save, or cost, compared with Sessions 09 to 12?

Then commit, tag, and update the project `README.md` with the `--audit` option:

```bash
git add .
git commit -m "Session 13: routing audit log"
git tag session-13
```

---

# Part B: Review an AI-generated pull request (AI-review)

The pull request's files are in the course repository's `projects/03-llm-application/session-13/review/`: a new module `src/incident_triage/duplicates.py`, its tests in `tests/unit/test_duplicates.py`, and the pull request description `PULL_REQUEST.md`. **Read them as you would a real pull request: as code someone wants merged into your project.**

## Setup

Put the pull request on its own branch, starting from your Part A result:

```bash
git switch -c review/duplicates session-13

# macOS / Linux / Git Bash
cp -r ~/python-ai-engineering-bridge/projects/03-llm-application/session-13/review/. .

# PowerShell
Copy-Item -Recurse -Force ~\python-ai-engineering-bridge\projects\03-llm-application\session-13\review\* .

git add .
git commit -m "PR: add duplicate detection (AI-generated)"
uv run pytest tests/unit/test_duplicates.py
```

The pull request's 8 tests pass, as its description says.

## Milestones

### Milestone B1: Review it yourself (45 min, no assistant)

Review **without** Claude Code first: this is the review you'd do on a colleague's pull request, and the one you'll compare the assistant's with.

1. Read `PULL_REQUEST.md`, then the code, then the tests. For each claim in the description, decide whether it's true, and how you'd check.
2. Run the code on realistic inputs: the sample reports in `data/reports.jsonl` (`load_reports` from `loading.py` reads them), small hand-made lists, edge cases. Use `python -W error::DeprecationWarning` for one run.
3. Write `PR-REVIEW.md` with your findings. For each one: what's wrong, **why it matters** to the on-call team, a **severity** (must fix, should fix, optional), and the **evidence**: a command and its output, or a test.
4. In `tests/unit/test_duplicates_review.py`, write a test for each of **at least five** findings that **fails** against the pull request's code and would pass once the finding is fixed.

### Milestone B2: Review it with Claude Code (20 min)

Start a **fresh** Claude Code session on the branch, in plan mode, and review only the pull request's commit:

```text
/code-review session-13..HEAD
```

Name the range: with no argument, `/code-review` compares the branch with its upstream or with `main`, which would include your Part A changes too. Then ask Claude Code to check every claim in `PULL_REQUEST.md`.

(Your review document is called `PR-REVIEW.md` rather than `REVIEW.md` on purpose: in repositories that use Anthropic's managed Code Review service on GitHub, `REVIEW.md` is a configuration file for that service.)

Add a section to `PR-REVIEW.md`:

- findings it reported that you'd missed (check each one: is it right?);
- findings you'd made that it missed;
- findings it reported that were **wrong** or not worth fixing;
- anything in the files that seemed to try to influence a reviewer, and whether the assistant was influenced by it.

### Milestone B3: Decide (10 min)

End `PR-REVIEW.md` with your decision, **approve**, **request changes** or **reject**, and a short message to the author: what must change before you'd approve, in priority order. Write it the way you'd want to receive it.

Commit `PR-REVIEW.md` and your tests on the review branch. **Don't merge the branch**, and don't fix the pull request's code: the review is the deliverable.

```bash
git add PR-REVIEW.md tests/unit/test_duplicates_review.py
git commit -m "Review of the duplicate-detection PR"
git switch session-13-audit
```

---

## Acceptance criteria

| Check | Expected result |
|---|---|
| On tag `session-13`: `uv run pytest tests/acceptance` | `188 passed`, with no API key and no network |
| On tag `session-13`: `uv run pytest tests/unit` | Your earlier tests plus at least 5 new ones pass |
| `git diff session-13-start session-13 -- tests/acceptance tests/conftest.py` | No output |
| `uv run incident-triage data/reports.jsonl --offline --route graph --audit out/audit.jsonl`, run twice | 24 lines in the log; no report text in it |
| `uv run incident-triage data/reports.jsonl --offline --audit out/audit.jsonl` | `error: --audit requires --route`; exit code `2` |
| `uv run ruff check .` and `uv run ruff format --check .` | Both pass |
| `CLAUDE.md` | Short, accurate, committed |
| On branch `review/duplicates`: `uv run pytest tests/unit/test_duplicates_review.py` | At least 5 tests, all **failing**, each linked to a finding in `PR-REVIEW.md` |
| `PR-REVIEW.md` | Findings with severity and evidence, the comparison with Claude Code's review, and a decision |
| `NOTES.md` | Your `CLAUDE.md` edits, the verified claims, your request and the plan, review findings, two failing-test proofs, and the answers from Milestone A6 |

## Debugging guidance

| You see | Where to look |
|---|---|
| Claude Code doesn't follow your `CLAUDE.md` | `/context`: is it loaded? Is it short enough that the important lines stand out? |
| The assistant edited `tests/acceptance/` | Revert those files (`git checkout session-13-start -- tests/acceptance`), and say in the request that they must not change. |
| `test_a_refusal` fails on the reasons | A4: a refusal's reason quotes the model, and the model can repeat the report. |
| `test_nothing_private_is_written` fails | Search the written line for the secret text: which field carried it? Error messages and refusal reasons are model output too. |
| `test_the_time_is_stored_in_utc` fails | Convert with `astimezone(UTC)`; comparing aware datetimes doesn't convert what's *stored*. |
| `test_cli_unwritable_audit_log` fails with a traceback | Opening a folder as a file raises an `OSError` subclass, and which one depends on the operating system. Catch `OSError`. |
| `test_cli_audit_needs_route` finds an audit file | Check `--audit` without `--route` **before** any work is done. |
| The session feels slow and the assistant repeats mistakes | The context is full. `/clear`, and start again with a precise request. |
| The assistant proposes a command you don't understand | Don't approve it. Ask what it does and why it's needed, or deny it. |
| No Claude Code access | Use an assistant your employer approves; Part B's first milestone needs no assistant at all. Note the substitution in `NOTES.md`. |

## Extension challenges (optional)

1. **A query tool.** Add `incident-triage audit-report out/audit.jsonl` (or a separate script) that answers "why was RPT-1001 paged?" and "how often did the LLM fail this week?" from the log. Use the assistant, and review it the same way.
2. **A hook.** Ask Claude Code to write a hook that runs `uv run ruff check` after every file edit. Read the [hooks guide](https://code.claude.com/docs/en/hooks-guide) first, and review the hook's configuration before enabling it: hooks run commands automatically.
3. **Writer and reviewer.** Implement a small change in one session, and review it with `/code-review` in a second, fresh one. Compare with reviewing it in the same session.
4. **Fix the pull request.** On a separate branch, fix the duplicate-detection module until your review tests pass, and make your own review of the fix.

## Reflection

Answer briefly in `NOTES.md`:

1. Where did the assistant save you the most time, and where did it cost you time?
2. Which of your Session 01 to 12 skills did you rely on most while reviewing?
3. What would you put in a team's rules for using coding assistants, based on this assignment?
4. How would you know, six months from now, whether code written this way is as maintainable as code written by hand?

## Deliverables

Submit **one** of the following, as your course instructions specify:

- a link to a Git repository containing the project, with the `session-13` tag and the `review/duplicates` branch (push only to a repository you own; keep it private if you prefer), **or**
- a `.zip` of the project folder, including `.git/`, **without** `.venv/`, `out/` and `.env`.

The submission must include:

- [ ] The audit log implemented, tagged `session-13`, with `CLAUDE.md` and the updated `README.md`
- [ ] `tests/acceptance/` and `tests/conftest.py` unchanged, and at least 5 new unit tests
- [ ] The `review/duplicates` branch with `PR-REVIEW.md` and at least 5 failing review tests
- [ ] `NOTES.md` with every item from the acceptance criteria and the reflection
- [ ] All acceptance criteria passing
