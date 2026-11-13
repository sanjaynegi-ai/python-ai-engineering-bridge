# Session 07 Assignment: Project 02 Becomes a Service

**Type:** Independent. Complete this without an AI coding assistant; Session 13 covers AI-assisted work.
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb), and your Session 06 work on Project 02
**Project:** **Project 02: Python API Service** (`incident-api`), stage 2 of 3

---

## Business scenario

Three Orbital Logistics (fictional) teams want the incident data **live**, not as last night's file:

- the **service desk** looks up single tickets while on the phone;
- **monitoring** creates tickets automatically when an alert fires;
- the **on-call dashboard** lists open tickets for one team, a page at a time, and shows the report.

You'll put the Project 02 code behind an HTTP API with FastAPI. The rules for a valid ticket already live in your `Ticket` model, so the API reuses them: a ticket submitted over HTTP is validated exactly like one read from an export file. The command line must keep working unchanged: the API is a second front end, not a rewrite.

## Learning objectives

By completing this assignment you will:

- **Design** a service layer that knows nothing about HTTP, and **test** it with plain pytest.
- **Implement** endpoints with path and query parameters, a request body, and response models.
- **Map** domain exceptions to `404` and `409` with exception handlers, and **rely** on FastAPI for `422`.
- **Inject** the service with `Depends`, and **override** it in a test.
- **Document** error responses so they appear in `/docs`.
- **Run** the service with `fastapi dev`, and **explain** the limits of an in-memory store.

## Prerequisites

- **Your Session 06 project** (`incident-api`, tagged `session-06`) with all 53 acceptance tests passing. This workbook adds to it; it doesn't replace it.
- The Session 07 concepts notebook.

---

## Project setup

### 1. Add the Session 07 files

The course repository has the new stubs and acceptance tests in `projects/02-python-api-service/session-07/`. Copy that folder's **contents** over your project; it only adds new files. Adjust the source path:

```bash
# macOS / Linux / Git Bash
cp -r ~/python-ai-engineering-bridge/projects/02-python-api-service/session-07/. ~/skillup/incident-api/

# PowerShell
Copy-Item -Recurse -Force ~\python-ai-engineering-bridge\projects\02-python-api-service\session-07\* ~\skillup\incident-api\
```

You should now have three new modules and six new test files:

| File | Status |
|---|---|
| `src/incident_api/service.py` | Stub: `TicketService`. Yours (Milestone 2) |
| `src/incident_api/schemas.py` | `Health` and `ErrorMessage` provided; the rest yours (Milestone 3) |
| `src/incident_api/api.py` | `get_service`, `/health` and `create_app` provided; routes and handlers yours (Milestones 4–6) |
| `tests/acceptance/conftest.py` | Provided: the `client` fixture. Don't edit |
| `tests/acceptance/test_service.py`, `test_schemas.py`, `test_api_read.py`, `test_api_write.py`, `test_api_docs.py` | Provided, one per milestone. Don't edit |

### 2. Add FastAPI

```bash
cd ~/skillup/incident-api
uv add "fastapi[standard]"
```

`fastapi[standard]` adds Uvicorn (the server), the `fastapi` command, and the test client's HTTP library. Then tell the `fastapi` command where your app is, by adding this at the end of `pyproject.toml`:

```toml
[tool.fastapi]
entrypoint = "incident_api.api:app"
```

### 3. Check the starting point

```bash
git add .
git commit -m "Session 07 starter files"
git tag session-07-start
uv run pytest
```

pytest stops with **2 collection errors**: `test_service.py` and `test_schemas.py` import names that don't exist yet. That's expected. Your Session 06 work is unaffected:

```bash
uv run pytest tests/acceptance/test_ticket.py tests/acceptance/test_settings.py tests/acceptance/test_rejection_and_loading.py tests/acceptance/test_report.py tests/acceptance/test_cli.py
```

should still report `53 passed`.

---

## Requirements

| # | Requirement |
|---|---|
| R1 | All 116 acceptance tests pass, unchanged: Session 06's 53 and Session 07's 63. |
| R2 | `service.py` imports nothing from FastAPI, and raises domain exceptions, never `HTTPException`. |
| R3 | Routes are thin: no business rules or filtering logic in `api.py`, only HTTP translation. |
| R4 | The endpoints, statuses and bodies are exactly as in the API table below. |
| R5 | `uv run incident-report` behaves exactly as in Session 06. |
| R6 | `uv run fastapi dev` starts the service, and `/docs` shows every endpoint, its parameters, and its `404`/`409` responses. |
| R7 | At least **10** test cases of your own in `tests/unit/`, including at least one that uses `app.dependency_overrides`. |
| R8 | `uv run ruff check .` and `uv run ruff format --check .` pass. |

### The API

| Method and path | Success | Errors |
|---|---|---|
| `GET /health` | `200` `{"status": "ok", "tickets": 10, "rejected": 6}` (provided) | none |
| `GET /report` | `200`, the `Report`, computed now from every ticket held | none |
| `GET /tickets` | `200`, a `TicketPage` | `422` for an invalid **or unknown** query parameter |
| `GET /tickets/{ticket_id}` | `200`, a `TicketOut` | `404` `{"detail": "ticket INC-9999 not found"}`; `422` if the id doesn't match `^INC-\d+$` |
| `POST /tickets` (body: a `Ticket`) | `201`, the stored ticket as a `TicketOut` | `409` `{"detail": "ticket INC-3001 already exists"}`; `422` if the body is invalid |

---

## Implementation milestones

### Milestone 1: Design before code

In `NOTES.md`, answer:

1. Which existing functions will the service call? Which will the API call **directly**? (Hint: ideally none.)
2. For each row of the API table, which **layer** produces each status code: Pydantic validation, the service (through an exception), or the route?
3. The service keeps tickets in memory. List two things that will go wrong because of that in production. (Part 9 of the notebook.)

### Milestone 2: The service layer

First, add two exceptions to `errors.py`:

- `TicketNotFoundError(ticket_id)`, with the message `ticket <id> not found` and a `ticket_id` attribute;
- `DuplicateTicketError(ticket_id)`, with the message `ticket <id> already exists` and a `ticket_id` attribute.

Then implement `TicketService` in `service.py`, following its docstrings. The design decisions to keep in mind:

- The **report** needs every valid record, duplicates included (`valid_records` is 11 for the sample data), but **lookups** need one ticket per id, the first one, as in the report's deduplication. So keep both: a list of records, and a dict by id.
- `find` keeps the order tickets were loaded or added. A dict preserves insertion order, so iterating it is enough.
- `get` must raise `TicketNotFoundError`, never `KeyError`. A `KeyError` escaping from the service would become a `500`.
- `add` appends to both the list and the dict, so that `/report` includes new tickets.

```bash
uv run pytest tests/acceptance/test_service.py
```

15 tests. Notice that none of them involves HTTP: business rules are tested where they live.

### Milestone 3: API schemas

In `schemas.py`, define:

| Model | Fields |
|---|---|
| `TicketOut` | `Ticket`'s eight fields, with `tags` as `list[str]`; plus `is_open: bool`, `breached: bool` and `sla_hours: int` (the SLA for its priority) |
| `TicketPage` | `total` (matching tickets, before paging), `limit`, `offset` (all `int`), `items: list[TicketOut]` |
| `TicketFilters` | `team: str \| None = None`, `priority: Priority \| None = None`, `open_only: bool = False`, `limit: int` from 1 to 100 (default 20), `offset: int` of 0 or more (default 0). **Unknown fields are rejected.** |

Also add the classmethod `TicketOut.from_ticket(ticket, *, sla_hours)`. `ticket.model_dump()` gives you the eight fields as keyword arguments.

Why not return `Ticket` directly? Because `TicketOut` is the **public contract**: it adds derived fields clients need, and the internal model can change without changing the API.

```bash
uv run pytest tests/acceptance/test_schemas.py
```

### Milestone 4: Read endpoints

In `api.py`, read the provided code first: `get_service`, `ServiceDep`, the `/health` route and `create_app`. Then add:

1. `GET /report` on `router`, tagged `"service"`. Pass `generated_at=datetime.now().astimezone()`.
2. `GET /tickets` on the `tickets` router: take `filters: Annotated[TicketFilters, Query()]` and the service; page the results of `service.find(...)` with `offset` and `limit`.
3. `GET /tickets/{ticket_id}`: validate the id with `Path(pattern=...)`, and declare `responses={404: {"model": ErrorMessage}}` so the `404` is documented.
4. An exception handler that turns `TicketNotFoundError` into `404` with `{"detail": str(error)}`, registered in `create_app` with `app.add_exception_handler`.

Every route returns a **model**, declared as its return type.

```bash
uv run pytest tests/acceptance/test_api_read.py
```

17 tests. If many fail at once, read the first failure's response body: `print(response.json())` in a quick test shows FastAPI's explanation.

### Milestone 5: Creating tickets

1. `POST /tickets` on the `tickets` router: the body is a `Ticket`; the status is `201`; the response is a `TicketOut`. Document `409` with `responses=`.
2. A handler that turns `DuplicateTicketError` into `409`.

You don't write any validation: the `Ticket` model already rejects bad ids, unknown priorities and a text `age_hours`, and FastAPI turns that into `422`. Check it by reading `test_api_write.py`'s parametrised test.

```bash
uv run pytest tests/acceptance/test_api_write.py
```

The last test in that file builds the app and **overrides** `get_service` with a hand-made service. Read it: it's the pattern for your own tests in Milestone 8.

### Milestone 6: Documentation and startup

```bash
uv run pytest tests/acceptance/test_api_docs.py
uv run pytest
```

These tests read the OpenAPI document: the title, paths, tags, query parameters, documented responses and schemas. If they pass, `/docs` is complete. One test checks that invalid settings stop the startup; the provided lifespan already does that.

All 116 acceptance tests should now pass.

### Milestone 7: Run it for real

Start the server:

```bash
uv run fastapi dev
```

Then open http://127.0.0.1:8000/docs in a browser and use **Try it out** to:

1. list open P1 tickets;
2. fetch `INC-3004` and `INC-9999`;
3. create a ticket, then create it again;
4. send a ticket with `"age_hours": "12"`.

Or, from a second terminal:

```bash
# macOS / Linux / Git Bash
curl -s "http://127.0.0.1:8000/tickets?team=database&open_only=true&limit=2"
curl -s -i http://127.0.0.1:8000/tickets/INC-9999
curl -s -i -X POST http://127.0.0.1:8000/tickets -H "Content-Type: application/json" \
  -d '{"id": "INC-3100", "title": "Printer queue stuck", "team": "it-support", "priority": "P4", "status": "open", "age_hours": 2, "assignee": null, "tags": ["printing"]}'
```

```powershell
# PowerShell
Invoke-RestMethod "http://127.0.0.1:8000/tickets?team=database&open_only=true&limit=2"
$body = '{"id": "INC-3100", "title": "Printer queue stuck", "team": "it-support", "priority": "P4", "status": "open", "age_hours": 2, "assignee": null, "tags": ["printing"]}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/tickets -ContentType "application/json" -Body $body
```

Now stop the server with `Ctrl+C`, start it again, and fetch `INC-3100`. Record what happens, and why, in `NOTES.md`.

Finally, start it with a broken setting and record what you see:

```bash
# Bash
INCIDENT_SLA_HOURS='{"P1": 30, "P2": 24, "P3": 72, "P4": 168}' uv run fastapi dev

# PowerShell
$env:INCIDENT_SLA_HOURS='{"P1": 30, "P2": 24, "P3": 72, "P4": 168}'; uv run fastapi dev
Remove-Item Env:INCIDENT_SLA_HOURS
```

### Milestone 8: Your own tests

Create `tests/unit/test_api.py` (or several files) with at least **10** test cases. At least one must use `app.dependency_overrides` with a `TicketService` you build by hand. Ideas:

- an empty service: `/tickets` returns `total` 0 and no items; `/report` still works;
- `limit=100` is accepted, `limit=101` isn't;
- `open_only` accepts `true`, `1`, `yes` and `on`;
- a lower-case id (`inc-3001`) is `422`, not `404`;
- a `POST` with four problems returns four errors, each with the right `loc`;
- a `POST` with an unknown extra field: accepted or rejected? Why?
- `DELETE /tickets/INC-3001` is `405`;
- the service directly: `find(team="")`, or `sla_hours` being a copy.

As before, prove that two of your tests can fail, and record the failures in `NOTES.md`.

### Milestone 9: Quality gate

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
uv run incident-report
git add .
git commit -m "Session 07: FastAPI service"
git tag session-07
```

---

## Acceptance criteria

| Check | Expected result |
|---|---|
| `uv run pytest tests/acceptance` | `116 passed` |
| `uv run pytest tests/unit` | Your Session 06 tests plus at least 10 new ones pass |
| `git grep -n -E "(from\|import) fastapi" -- src/incident_api/service.py` | No output: the service layer doesn't import FastAPI |
| `uv run fastapi dev`, then `/docs` | Five endpoints; `404` and `409` documented |
| `uv run incident-report` | Same output and exit code `1` as in Session 06 |
| `git diff session-06 -- src/incident_api/models.py src/incident_api/loading.py src/incident_api/summary.py src/incident_api/report.py` | No output: the domain code didn't change |
| `git diff session-07-start -- tests/acceptance` | No output: the provided tests are unchanged |
| `uv run ruff check .` and `uv run ruff format --check .` | Both pass |
| `NOTES.md` | Milestones 1, 7 and 8, and the reflection |

## Debugging guidance

| You see | Where to look |
|---|---|
| `ImportError: cannot import name 'TicketOut'` during collection | You haven't reached that milestone. Run only the current milestone's test file. |
| Every API test errors with `NotImplementedError` | The `client` fixture starts the app, which calls `TicketService.from_exports`. Finish Milestone 2 first. |
| `AttributeError: 'State' object has no attribute 'service'` | A `TestClient` used without `with`, so startup didn't run. |
| A `KeyError` in a test traceback | `service.get` let a `KeyError` escape. Raise `TicketNotFoundError`. |
| `500` instead of `404` or `409` | The handler isn't registered in `create_app`, or is registered for a different exception class. |
| `200` instead of `201` | `status_code=` is missing from the `POST` decorator. |
| `?teem=x` returns `200` | `TicketFilters` doesn't forbid extra fields. |
| `total` is wrong on later pages | Count the matches **before** slicing. |
| `test_create_documents_201_and_409` fails | `responses={409: {"model": ErrorMessage}}` on the `POST` route. |
| `fastapi dev` says it can't find the app | The `[tool.fastapi]` entrypoint in `pyproject.toml`, and that you run it from the project folder. |
| `UnicodeEncodeError` from `fastapi dev` on Windows | Its banner uses emoji. Use Windows Terminal, or set `PYTHONIOENCODING=utf-8`, or start the server with `uv run uvicorn incident_api.api:app --reload`. |
| `[Errno 10048]` or "address already in use" | Another server is still running on port 8000. Stop it, or add `--port 8001`. |

## Extension challenges (optional)

1. **`Location` header.** Return `Location: /tickets/<id>` with the `201`, as REST conventions suggest. (Hint: a `response: Response` parameter.) Test it.
2. **API key.** Require an `X-API-Key` header on `POST /tickets` only, with the valid key in a new `INCIDENT_API_KEY` setting stored as `SecretStr`. Return `401` without it. Make sure the key never appears in `/docs`, logs or error bodies.
3. **Logging.** Configure `logging` so that the service's startup message ("loaded N tickets ...") appears in the `fastapi dev` output. Where should that configuration live, and why not in `service.py`?
4. **`PATCH /tickets/{id}`.** Allow updating `status` and `assignee` only. Which status code for an unknown id? For an attempt to change `priority`?
5. **Two workers.** Run `uv run fastapi run --workers 2`, create a ticket, and fetch it a few times. Explain the results.

## Reflection

Answer briefly in `NOTES.md`:

1. Which status code decisions were obvious, and which needed thought?
2. Your API reuses the `Ticket` model as its request body. When would you want a separate request model?
3. What would you need to change to store tickets in a database instead of memory? Which layers would change, and which wouldn't?
4. How does this compare with building the same API in Spring Boot, ASP.NET Core or Express?

## Deliverables

Submit **one** of the following, as your course instructions specify:

- a link to a Git repository containing the project, with the `session-07` tag (push only to a repository you own; keep it private if you prefer), **or**
- a `.zip` of the project folder **without** `.venv/`, `out/` and `.env`.

The submission must include:

- [ ] `service.py`, `schemas.py` and `api.py` implemented, and the two exceptions in `errors.py`
- [ ] `tests/acceptance/` unchanged, and your `tests/unit/` with at least 10 new test cases
- [ ] `NOTES.md` with your milestone answers and the reflection
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
