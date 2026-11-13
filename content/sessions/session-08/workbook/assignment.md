# Session 08 Assignment: The On-Call Dashboard, Concurrently

**Type:** Independent. Complete this without an AI coding assistant; Session 13 covers AI-assisted work.
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb) and [`03-async-debugging-lab.ipynb`](../notebooks/03-async-debugging-lab.ipynb); your Session 07 work on Project 02; your Session 05 `asset-lookup` client
**Project:** **Project 02: Python API Service** (`incident-api`), stage 3 of 3. **Completing this workbook completes Project 02 (Milestone 2).**

---

## Business scenario

The Orbital Logistics (fictional) on-call engineers open one page at the start of every shift: the **dashboard**. For each team it shows the open and breached tickets **and the assets the team owns**, so that when `INC-3002` mentions "the backup job", the engineer can see at a glance which systems that team runs.

The assets live in the **Asset Inventory API** you wrote a client for in Session 05. Each team needs one HTTP call (more if the list is paginated), and the inventory takes about half a second to answer. Four teams, one after another, would make the page take over two seconds, and the company plans to split into more teams next quarter.

Two more requirements from the on-call team:

- If the inventory is slow or down for one team, the dashboard must **still show everything else**, and say what's missing. A dashboard that fails completely when one dependency hiccups is useless during an incident, which is exactly when dependencies hiccup.
- The service must never hang: every call to the inventory has a deadline.

## Learning objectives

By completing this assignment you will:

- **Convert** a synchronous HTTP client into an asynchronous one with `httpx.AsyncClient`.
- **Fetch** several resources concurrently with `asyncio.gather`, and **prove** the concurrency in tests.
- **Apply** a deadline per operation with `asyncio.timeout`, and **handle** partial failure deliberately.
- **Share** one async client across an application, created and closed by the FastAPI lifespan.
- **Write** an `async def` endpoint, and **test** async code with pytest-asyncio.
- **Measure** the difference between sequential and concurrent I/O on a real server.

## Prerequisites

- **Your Session 07 project** (`incident-api`, tagged `session-07`) with all 116 acceptance tests passing.
- Your Session 05 `asset-lookup` project, for reference: you'll port its client.
- The Session 08 concepts notebook and debugging lab.

---

## Project setup

### 1. Add the Session 08 files

Copy the **contents** of the course repository's `projects/02-python-api-service/session-08/` over your project, adjusting the source path:

```bash
# macOS / Linux / Git Bash
cp -r ~/python-ai-engineering-bridge/projects/02-python-api-service/session-08/. ~/skillup/incident-api/

# PowerShell
Copy-Item -Recurse -Force ~\python-ai-engineering-bridge\projects\02-python-api-service\session-08\* ~\skillup\incident-api\
```

| File | Status |
|---|---|
| `src/incident_api/inventory.py` | Stub. The constructor and closing methods are provided; `Asset`, `from_settings` and `team_assets` are yours (Milestone 3) |
| `src/incident_api/dashboard.py` | The models are provided; the three functions are yours (Milestone 4) |
| `fake_inventory_server.py` | Provided: Session 05's fake inventory, with a new `--latency` option |
| `.env.example` | Updated: documents the four new settings (replaces the old one) |
| `tests/conftest.py` | Updated: `clean_env` now clears every `INCIDENT_*` variable, and a new `fake_inventory` fixture (replaces the old one). Don't edit |
| `tests/acceptance/test_inventory_settings.py`, `test_inventory.py`, `test_dashboard.py`, `test_api_dashboard.py` | Provided, one per milestone. Don't edit |

You'll also edit `errors.py`, `settings.py` and `api.py`.

### 2. Add the dependencies

```bash
cd ~/skillup/incident-api
uv add httpx
uv add --dev pytest-asyncio
```

`httpx` is already installed (FastAPI's test client needs it), but your code now imports it directly, so declare it. `pytest-asyncio` runs `async def` tests.

### 3. Check the starting point

```bash
git add .
git commit -m "Session 08 starter files"
git tag session-08-start
uv run pytest
```

pytest stops with **4 collection errors**, one per new test file. Your earlier work is unaffected:

```bash
uv run pytest tests/acceptance --ignore-glob="*inventory*" --ignore-glob="*dashboard*"
```

should report `116 passed`.

---

## Requirements

| # | Requirement |
|---|---|
| R1 | All 164 acceptance tests pass, unchanged: 116 from Sessions 06–07 and 48 new. |
| R2 | Teams are fetched **concurrently**; the pages of **one** team are fetched one after another. |
| R3 | Every team has its own deadline (`INCIDENT_INVENTORY_DEADLINE_SECONDS`), and every HTTP request has a timeout (`INCIDENT_INVENTORY_TIMEOUT_SECONDS`). |
| R4 | Inventory failures for a team appear as that team's `inventory_error`; `GET /dashboard` still answers `200`. Unexpected exceptions (bugs) are **not** caught. |
| R5 | One `InventoryClient` per application, created at startup and closed at shutdown; none without a token. |
| R6 | No blocking calls inside `async def` code: no `time.sleep`, no `httpx.Client`, no `requests`. |
| R7 | At least **8** async test cases of your own in `tests/unit/`. |
| R8 | `uv run ruff check .` and `uv run ruff format --check .` pass. |

### The new endpoint

`GET /dashboard` (tag `service`) returns a `Dashboard`: `generated_at`, and `teams`, one `TeamDashboard` per team that has tickets, in alphabetical order:

```json
{
  "team": "database",
  "open": 4, "breached": 2, "unassigned_open": 2, "oldest_open_hours": 80,
  "assets": [{"id": "db-03", "name": "Orders database replica", "type": "database",
              "team": "database", "environment": "production", "criticality": "high"}],
  "inventory_error": null
}
```

Exactly one of `assets` and `inventory_error` is set. Without a configured token, every team has `"inventory_error": "inventory not configured"`.

---

## Implementation milestones

### Milestone 1: Predict

Before writing code, answer in `NOTES.md`:

1. With the inventory answering in 0.5 s, how long would the dashboard take for 4 teams sequentially? Concurrently? For 40 teams, both ways?
2. Which of your Session 05 client's methods do the waiting? Which lines will need `await`?
3. The dashboard must work when the inventory fails for one team. Which concepts-notebook pattern (Part 5) fits, and why not the others?

You'll check your answers in Milestone 6.

### Milestone 2: Settings and errors

1. In `errors.py`, add `InventoryError`, and two subclasses of it: `InventoryUnavailable` and `InventoryAuthError` (the same family as Session 05's).
2. In `settings.py`, add four fields, read from `INCIDENT_INVENTORY_*` variables:

   | Field | Type and default |
   |---|---|
   | `inventory_base_url` | `str`, `"http://127.0.0.1:8765"` |
   | `inventory_token` | `SecretStr \| None`, `None` |
   | `inventory_timeout_seconds` | `PositiveFloat`, `5.0`: per HTTP request |
   | `inventory_deadline_seconds` | `PositiveFloat`, `10.0`: per team, all pages together |

```bash
uv run pytest tests/acceptance/test_inventory_settings.py
```

### Milestone 3: The asynchronous client

In `inventory.py`:

1. `Asset`: a frozen Pydantic model with six `str` fields (`id`, `name`, `type`, `team`, `environment`, `criticality`). It replaces Session 05's dataclass and its hand-written `from_json`.
2. `InventoryClient.from_settings(settings, *, transport=None)`: `None` without a token; otherwise a client built from the settings.
3. `async def team_assets(self, team, *, page_size=50) -> list[Asset]`: port Session 05's `list_assets`, filtered by team, following the pagination. The errors map as before:

   | Situation | Raise |
   |---|---|
   | `401` or `403` | `InventoryAuthError` |
   | A timeout, a refused connection, or a `5xx` | `InventoryUnavailable` |
   | Any other status, invalid JSON, a page without `items`/`total`, an asset of the wrong shape | `InventoryError` |

Hints:

- Most of the port is adding `await` in front of `self._http.request(...)`, and `async` in front of the methods that call it. Nothing else about HTTP changes.
- `httpx.TimeoutException` is a subclass of `httpx.TransportError`. If you catch both separately, catch the timeout first.
- `Asset.model_validate(item)` raises `pydantic.ValidationError`: turn it into `InventoryError`, so callers deal with one family of exceptions.
- Pages depend on each other (you only know whether to fetch page 2 after reading page 1), so they're fetched **one at a time**. One test checks that.

```bash
uv run pytest tests/acceptance/test_inventory.py
```

17 tests, all `async def`. Open the file and notice `pytestmark = pytest.mark.asyncio` at the top. Then read `FakeInventory` in `tests/conftest.py`: it counts the requests in flight, which is how the next milestone's tests prove concurrency without measuring time.

### Milestone 4: Concurrency, deadlines and partial failure

In `dashboard.py`, implement the three functions, following their docstrings:

1. **`fetch_one_team(client, team, *, deadline)`**: fetch one team's assets inside `async with asyncio.timeout(deadline)`. Turn a `TimeoutError` into `TeamAssets(error="inventory did not answer within <deadline>s")` (format the number with `:g`, so `0.3` prints as `0.3` and `10.0` as `10`), and an `InventoryError` into `TeamAssets(error=str(error))`. Let **any other** exception propagate.
2. **`fetch_team_assets(client, teams, *, deadline)`**: all teams **concurrently**, results in the order of `teams`. One line with `asyncio.gather`.
3. **`build_dashboard(service, client, *, deadline, generated_at)`**: build the report with `service.report(...)`, take its teams in alphabetical order, fetch their assets (or, with no client, mark them all `"inventory not configured"` without any requests), and combine each team's `TeamStats` with its `TeamAssets` into a `TeamDashboard`.

```bash
uv run pytest tests/acceptance/test_dashboard.py
```

Read the test names before you start: they're the requirements in executable form. `test_unexpected_exceptions_are_not_swallowed` fails if you catch `Exception`; `test_a_slow_team_is_cut_off_at_its_deadline` fails if you put one deadline around the whole `gather` instead of one per team. Make sure you understand why each design would be wrong.

### Milestone 5: The endpoint and the shared client

In `api.py`:

1. Two new dependencies, like `get_service`: `get_inventory(request)` returns `request.app.state.inventory` (an `InventoryClient` or `None`), and `get_settings(request)` returns `request.app.state.settings`.
2. In the lifespan: store the settings on `app.state.settings`; create the client with `InventoryClient.from_settings(...)` and store it on `app.state.inventory`; and make sure it's **closed** at shutdown, even if something fails. Put `yield` in a `try` and close the client in `finally`.
3. `GET /dashboard` on `router`, tagged `"service"`: an **`async def`** endpoint that awaits `build_dashboard(...)` with the deadline from the settings and `generated_at=datetime.now().astimezone()`.

```bash
uv run pytest tests/acceptance/test_api_dashboard.py
uv run pytest
```

All 164 acceptance tests should pass. Note that the endpoint tests use the synchronous `TestClient`, as in Session 07, even though the endpoint is `async def`: `TestClient` runs the app's event loop for you.

### Milestone 6: Run it and measure

In one terminal, start the fake inventory with half a second of latency:

```bash
uv run python fake_inventory_server.py --latency 0.5
```

In `.env` (copy `.env.example` if you don't have one), set `INCIDENT_INVENTORY_TOKEN=local-dev-token`, the fake's default token. In a second terminal:

```bash
uv run fastapi dev
```

Open http://127.0.0.1:8000/dashboard, or time it from a third terminal:

```bash
# macOS / Linux / Git Bash
curl -s -o /dev/null -w "%{time_total}s\n" http://127.0.0.1:8000/dashboard

# PowerShell
(Measure-Command { Invoke-RestMethod http://127.0.0.1:8000/dashboard }).TotalSeconds
```

Run it a few times. On the course's test machine it took about **0.8 s**. Now make `fetch_team_assets` sequential **temporarily**:

```python
return [await fetch_one_team(client, team, deadline=deadline) for team in teams]
```

Measure again (about **2.3 s** on the test machine), run `uv run pytest tests/acceptance/test_dashboard.py` to see which tests catch it, and **revert** the change. Then:

- stop the fake inventory, and reload the dashboard: what does each team show, and how long does it take?
- restart it with `--latency 15`: what happens now, and after how long?

Record all your measurements and observations in `NOTES.md`, next to your Milestone 1 predictions.

### Milestone 7: Your own tests

Create `tests/unit/test_async.py` with at least **8** async test cases (`pytestmark = pytest.mark.asyncio`). The `fake_inventory` fixture is available to them. Ideas:

- a team whose page has an empty `items` list but a wrong `total`: does your loop stop?
- `team_assets` with a team name that contains a space;
- the same team listed twice in `fetch_team_assets`;
- a deadline shorter than the fake's latency: every team times out, and the total time is about the deadline;
- an `InventoryAuthError` message is what `inventory_error` shows;
- cancelling a `fetch_team_assets` task from outside (`task.cancel()`): does `CancelledError` propagate, and are no requests left in flight?
- `fake_inventory.failures[team] = "garbage"` for one team in a dashboard.

As before, prove that two of your tests can fail, and record the failures in `NOTES.md`.

### Milestone 8: Project 02 complete

This is the end of Project 02. Update your project's `README.md` so that a new team member could run it: the endpoints (including `/dashboard`), the settings, how to run the fake inventory, and the known limitations (in-memory tickets, one process). Then:

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
git add .
git commit -m "Session 08: concurrent dashboard; Project 02 complete"
git tag session-08
git tag project-02
```

---

## Acceptance criteria

| Check | Expected result |
|---|---|
| `uv run pytest tests/acceptance` | `164 passed` |
| `uv run pytest tests/unit` | Your earlier tests plus at least 8 new async ones pass |
| `git grep -n -E "time\.sleep\|import requests\|httpx\.Client\(" -- src` | No output: nothing blocks the event loop |
| `git diff session-08-start -- tests/acceptance tests/conftest.py` | No output: the provided tests are unchanged |
| `GET /dashboard` with the fake inventory at `--latency 0.5` | Well under 2 seconds; every team has assets |
| `GET /dashboard` with the fake inventory stopped | `200`; every team has an `inventory_error`; no traceback in the server log |
| `uv run incident-report` | Unchanged from Session 06: exit code `1` |
| `uv run ruff check .` and `uv run ruff format --check .` | Both pass |
| `NOTES.md` | Milestones 1, 6 and 7, and the reflection |
| `README.md` | Describes the finished service |

## Debugging guidance

| You see | Where to look |
|---|---|
| `TypeError: object of type 'coroutine' has no len()`, or "coroutine ... was never awaited" | A missing `await` (lab 1). |
| `Failed: async def functions are not natively supported` | The test file or test lacks `@pytest.mark.asyncio`, or `pytest-asyncio` isn't installed (`uv add --dev pytest-asyncio`). |
| `test_teams_are_fetched_concurrently` fails with `peak_in_flight == 1` | You await the teams one by one. Use `asyncio.gather`. |
| `test_a_slow_team_is_cut_off_at_its_deadline`: every team times out | One `asyncio.timeout` around the whole `gather`. Put it inside `fetch_one_team`, around one team. |
| `test_unexpected_exceptions_are_not_swallowed` fails | You catch `Exception`. Catch `TimeoutError` and `InventoryError` only. |
| A `ValidationError` escapes from `team_assets` | Convert it to `InventoryError` where you parse the page. |
| `RuntimeError: Cannot send a request, as the client has been closed` | The client was closed too early, or a test uses it after its `async with` block. |
| `test_one_client_is_created_at_startup_and_closed_at_shutdown` fails | Close the client in the lifespan's `finally`, after `yield`. |
| `RuntimeError: asyncio.run() cannot be called from a running event loop` | Lab 4: inside async code, `await` instead. |
| `/dashboard` takes about `latency × teams` on the real server | Something is still sequential, or blocking. Check for `time.sleep` or a sync client. |
| Every team shows `401` on the real server | `INCIDENT_INVENTORY_TOKEN` doesn't match the fake's token (`local-dev-token` by default). |
| Every team shows "All connection attempts failed" | The fake inventory isn't running, or `INCIDENT_INVENTORY_BASE_URL` points elsewhere. |

## Extension challenges (optional)

1. **Limit concurrency.** Add `INCIDENT_INVENTORY_MAX_CONCURRENCY` (default 10), and enforce it with one shared `asyncio.Semaphore`. Write a test with `fake_inventory.peak_in_flight` that proves the limit with 20 teams.
2. **Retry once.** Retry `InventoryUnavailable` once, after a short `await asyncio.sleep`, within the same deadline. Which errors should never be retried?
3. **`TaskGroup` version.** Rewrite `fetch_team_assets` with `asyncio.TaskGroup`. What has to change in `fetch_one_team` for the behaviour to stay the same, and why?
4. **Cache.** Cache each team's assets for 60 seconds, so that refreshing the dashboard doesn't call the inventory every time. Watch out for two requests filling the same cache entry at once.
5. **An async ticket service?** Would making `TicketService` asynchronous help anything? Explain your answer in `NOTES.md`.

## Reflection

Answer briefly in `NOTES.md`:

1. Where did the time go before and after concurrency, and how close were your Milestone 1 predictions?
2. Why is the deadline per team rather than one for the whole dashboard? When would one overall deadline be better?
3. What would happen to the other users of the service if `team_assets` used `httpx.Client` instead of `AsyncClient`, inside the `async def` endpoint?
4. Compare Python's `asyncio` with what you use in Java, C# or JavaScript. What surprised you?

## Deliverables

Submit **one** of the following, as your course instructions specify:

- a link to a Git repository containing the project, with the `session-08` and `project-02` tags (push only to a repository you own; keep it private if you prefer), **or**
- a `.zip` of the project folder **without** `.venv/`, `out/` and `.env`.

The submission must include:

- [ ] `inventory.py` and `dashboard.py` implemented; `errors.py`, `settings.py` and `api.py` extended
- [ ] `tests/acceptance/` and `tests/conftest.py` unchanged, and your `tests/unit/` with at least 8 new async test cases
- [ ] `NOTES.md` with your predictions, measurements, milestone answers and the reflection
- [ ] An updated `README.md` for the finished service
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
