# Final Readiness Assessment: `swap-desk`

**Time:** 60 minutes · **Points:** 100 · **Type:** **Independent**: no AI coding assistants

On-call engineers at Orbital Logistics (a fictional company) sometimes swap on-call weeks with a colleague. The team wants a small service for it: a rota check, a swap request API, and an LLM summary of the handover note each engineer writes at the end of a week. You'll finish an unfinished version of that service.

The six tasks follow the course's readiness competencies. Their points match the weights in [`../python-readiness.md`](../python-readiness.md). They're independent: if you're stuck on one, move on and come back.

| Task | Competency | Points | Suggested time |
|---|---|---:|---:|
| 1 | Project structure and dependencies | 15 | 5 min |
| 2 | Python fundamentals | 20 | 12 min |
| 3 | APIs and Pydantic | 20 | 15 min |
| 4 | LLM integration | 20 | 12 min |
| 5 | Testing and debugging | 15 | 10 min |
| 6 | Engineering explanation | 10 | 6 min |

## Rules

- Work alone. Don't use AI coding assistants or AI chat tools, including the ones built into your editor: switch them off before you start.
- You may use the official documentation of Python, uv, pytest, Pydantic, FastAPI and the OpenAI SDK, the course repository, and your own notes and projects.
- Don't edit the provided tests (`tests/conftest.py` and `tests/test_task*.py`).
- Commit when time is up, even if some tasks are unfinished. Partial work earns partial points.

## Setup

```bash
# macOS / Linux / Git Bash
cp -r ~/python-ai-engineering-bridge/assessments/final-assessment ~/skillup/swap-desk

# PowerShell
Copy-Item -Recurse ~\python-ai-engineering-bridge\assessments\final-assessment ~\skillup\swap-desk
```

```bash
cd ~/skillup/swap-desk
git init
git add .
git commit -m "Assessment starter"
uv sync
```

## Task 1: Make the project runnable (15 points)

The tests can't run yet, and neither can the command.

1. Add **pytest** and **Ruff** as **development** dependencies (not runtime ones), so that `uv run pytest` works and the lockfile records them.
   If PyPI isn't reachable, add `--offline`: uv then uses the packages it downloaded for your earlier projects.
2. `uv run swap-desk breaches data/rota.json` fails before any of the project's code runs. Find out why from the error, and fix the project configuration (not the code). Once it's fixed, the command reaches `rota.py` and stops with `NotImplementedError` until you've done Task 2; after that it prints the engineers who are on call more than two weeks in a row, and exits with code 1 because some are.

Done when `uv run pytest tests/test_task1_project.py` passes.

## Task 2: The rota (20 points)

Implement the three functions in `src/swap_desk/rota.py`; their docstrings are the specification. `data/rota.json` is a sample. The on-call policy allows **at most two consecutive weeks**: three weeks in a row is a breach.

Done when `uv run pytest tests/test_task2_rota.py` passes.

## Task 3: Swap requests over HTTP (20 points)

In `src/swap_desk/models.py`, define `SwapRequest`, a Pydantic model with these fields and rules:

| Field | Type and rules |
|---|---|
| `requester`, `colleague` | strings of 1 to 50 characters, stripped of surrounding spaces; blank isn't allowed |
| `team` | one of `platform`, `database`, `network`, `it-support` (the `Team` type) |
| `week` | a date, which must be a **Monday** |
| `submitted_at` | a **timezone-aware** datetime |

Rules across fields: the requester and the colleague must be different people (compare names ignoring case), and the request must be submitted **at least 24 hours before the week starts**, on Monday at 09:00 UTC (`WEEK_START_TIME`). Exactly 24 hours before is allowed. Every rule violation must be a validation error.

Then define `StoredSwap`: a `SwapRequest` plus `id: int`.

In `src/swap_desk/api.py`, implement `create_app()`, with an in-memory store per app:

- `POST /swaps` with a `SwapRequest` body: **201**, and the stored swap as JSON. IDs start at 1. An invalid request is **422** and isn't stored.
- `GET /swaps`: every stored swap, in the order they were created; `GET /swaps?team=network` only that team's.
- `GET /swaps/{id}`: that swap, or **404**.

Done when `uv run pytest tests/test_task3_api.py` passes.

## Task 4: Summarise a handover note (20 points)

Implement `summarise_handover` in `src/swap_desk/handover.py` with the OpenAI SDK's Responses API and structured output, as in Session 09. The docstring lists exactly which failures are `HandoverError`s and which aren't. The tests use a fake API (`fake_openai` in `tests/conftest.py`): no key and no network.

Done when `uv run pytest tests/test_task4_handover.py` passes.

## Task 5: Debug and test (15 points)

1. `tests/test_task5_deadlines.py` fails. Find and fix the problems in `src/swap_desk/deadlines.py` (there's more than one). Don't change the tests.
2. Write `tests/test_my_streaks.py` with **at least three tests of your own** for `longest_streak`. They'll be run against several incorrect versions of `longest_streak`: the more of them your tests catch, the more points you get. Tests that fail on a correct `longest_streak` earn nothing.

## Task 6: Explain (10 points)

Answer the four questions in `EXPLANATION.md`, in your own words: a few sentences each.

## How it's scored

- **Tasks 1 to 4:** the share of tests that pass, counting the provided tests **and further tests of the same requirements** that you don't see. Read the specifications, not just the tests.
- **Task 5:** 60% for the fixed deadlines (provided and further tests), 40% for how many incorrect versions your own tests catch.
- **Task 6:** marked by hand, for accuracy and reasoning, not length.

The suggested readiness threshold is 80 points in total, together with the capstone; see [`../python-readiness.md`](../python-readiness.md).
