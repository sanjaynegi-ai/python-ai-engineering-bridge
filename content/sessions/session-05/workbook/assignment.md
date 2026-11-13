# Session 05 Assignment: An Asset Inventory Client

**Type:** Independent. Complete this without an AI coding assistant; Session 13 covers AI-assisted work.
**Estimated time:** 2–2.5 hours
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb), and the package structure and pytest skills from Session 04

---

## Business scenario

The Orbital Logistics (fictional) infrastructure team runs an **Asset Inventory** API: every server, database, network device and badge reader, with its owning team and criticality. The on-call tooling needs it. Session 07's incident API will enrich tickets with it, and today the on-call engineers want a quick command-line lookup.

Your job is the **client**: a small, well-tested package that every other tool can use, so that no one else has to think about URLs, tokens, timeouts or status codes again. The infrastructure team has been clear about three things:

- their service is redeployed most nights and is unavailable for a few minutes, so **every call needs a timeout** and a clear "unavailable" error;
- tokens are personal and **must never appear in code, logs or error messages**;
- please don't hammer the real service from tests.

You'll work against a **fake inventory** that ships with the starter, and test everything with respx.

## Learning objectives

By completing this assignment you will:

- **Implement** an API client class around one reusable `httpx.Client`, with a base URL, an auth header and a timeout.
- **Translate** HTTP status codes and transport failures into a small set of domain exceptions, chaining the original cause.
- **Follow** pagination to return complete results.
- **Load** configuration from environment variables and `.env`, and **keep** the token out of code, `repr()` and messages.
- **Test** the client with respx, covering success, 4xx, 5xx, timeouts and connection errors, without a network.

## Prerequisites

- Session 04: a `src/`-layout package, dataclasses and pytest fixtures are assumed.
- The Session 05 concepts notebook.

---

## Project setup

Copy the starter project out of the course repository, adjusting the source path to where you cloned the course:

```bash
# macOS / Linux / Git Bash
cp -r ~/python-ai-engineering-bridge/sessions/session-05/workbook/starter ~/skillup/asset-lookup

# PowerShell
Copy-Item -Recurse ~\python-ai-engineering-bridge\sessions\session-05\workbook\starter ~\skillup\asset-lookup
```

Then:

```bash
cd ~/skillup/asset-lookup
git init
git add .
git commit -m "asset-lookup starter"
git tag starter
uv sync
cp .env.example .env        # PowerShell: Copy-Item .env.example .env
```

Edit `.env` and set `INVENTORY_API_TOKEN=local-dev-token`, the token the fake server accepts. Then confirm that Git ignores it:

```bash
git check-ignore .env      # prints ".env"; if it prints nothing, stop and fix .gitignore
```

Read the starter's `README.md`: it documents the API you're writing a client for. Then run the tests:

```bash
uv run pytest
```

Six tests already pass. They test the provided `Asset` model; everything else fails until you implement `settings.py` and `client.py`. The files `errors.py`, `models.py` and `cli.py` are provided: read them, but you shouldn't need to change them.

---

## Requirements

| # | Requirement |
|---|---|
| R1 | All 46 acceptance tests in `tests/acceptance/` pass, unchanged. Some of them start the fake server themselves on a free port, so they also prove your client works over real HTTP. |
| R2 | `InventoryClient` creates exactly **one** `httpx.Client`, with the base URL, `Authorization: Bearer <token>`, `Accept: application/json` and the configured timeout, and closes it when used as a context manager. |
| R3 | Status codes and failures map to the error contract in `client.py`'s docstring. Transport failures are chained (`raise ... from error`). |
| R4 | `list_assets` returns **every** matching asset, following pagination, and sends `team` only when one is given. |
| R5 | `load_settings` reads the environment (and `./.env` when called without arguments), applies the documented defaults, and raises `SettingsError` naming the variable that's wrong. Existing environment variables win over `.env`. |
| R6 | The token never appears in `repr(settings)`, in exception messages, or in CLI output. `.env` is never committed. |
| R7 | You add **at least 10 test cases** of your own in `tests/unit/`, using respx, including at least one status code or edge case that the acceptance tests don't cover. |
| R8 | `uv run ruff check .` and `uv run ruff format --check .` pass. |

---

## Implementation milestones

### Milestone 1: Explore the API by hand (15 min)

Start the fake server in its own terminal, and leave it running for the rest of the assignment:

```bash
uv run python fake_inventory_server.py
```

In a second terminal, open an interactive session with `uv run python` and use HTTPX directly, exactly as in Part 2 of the concepts notebook. Find out, and note in `NOTES.md`:

1. What does `GET /assets/db-03` return **without** a token? With the wrong one? With the right one?
2. How many assets does the platform team have, and how many requests does it take to fetch them all with `page_size=2`?
3. What do `broken-01` and `slow-01` do? What happens to `slow-01` with `timeout=1`?
4. What does `POST /assets/db-03/notes` return without a `"text"` field?

Watch the server terminal while you do this: it prints one line per request.

### Milestone 2: `settings.py` (20 min)

Implement `load_settings` as its docstring describes. Two details matter:

- Call `load_dotenv(Path.cwd() / ".env")` when `env` is `None`. Passing an explicit path makes the behaviour predictable; without one, python-dotenv searches for a file in ways that depend on where the calling code lives.
- `env.get(...)` works for both a plain dict (used by tests) and `os.environ`, because both are mappings.

```bash
uv run pytest tests/acceptance/test_settings_and_models.py
```

### Milestone 3: The client and `get_asset` (35 min)

- `__init__` creates **one** `httpx.Client` and keeps it in an attribute such as `self._http`.
- `from_settings` is a `@classmethod`, like `Ticket.from_record` in Session 04.
- `__enter__` returns `self`; `__exit__` calls `close()`.
- For `get_asset`, write one private helper, for example `_request(method, path, **kwargs)`, that sends the request and handles the things **every** endpoint shares: transport failures, `401`/`403` and `5xx`. Then the method itself only deals with what's specific to it (`404` means `AssetNotFound`, and `200` means parse an `Asset`).
- Remember the ordering lesson from the quiz: `httpx.TimeoutException` is a subclass of `httpx.TransportError`.
- Invalid JSON and a wrong shape must become `InventoryError`, not crash with a `KeyError` or `JSONDecodeError`. `Asset.from_json` already checks the shape.

Run `uv run pytest tests/acceptance/test_client.py` as you go. The pagination and note tests keep failing until Milestones 4 and 5; everything else in that file should pass by the end of this milestone.

### Milestone 4: `list_assets` and pagination (20 min)

Request page 1, then page 2, and so on, collecting `items`, until you have `total` assets **or** a page comes back empty. (Why both conditions? What could go wrong if you relied on `total` alone?)

Build `params` as a dict, and add `team` only when it isn't `None`.

### Milestone 5: `add_note` (15 min)

`POST` the JSON body `{"text": ..., "ticket_id": ...}`. `201` returns the new note's integer `id`; `404` is `AssetNotFound`; anything else unexpected, such as `422`, is `InventoryError`, not "unavailable".

**Think about it, and answer in `NOTES.md`:** should `add_note` retry after a `ReadTimeout`? Why not?

All acceptance tests should now pass. Commit.

### Milestone 6: Use the real thing (10 min)

With the fake server running:

```bash
uv run asset-lookup show db-03
uv run asset-lookup list --team network
uv run asset-lookup note db-03 "Disk replaced" --ticket INC-3004
uv run asset-lookup show nope
uv run asset-lookup show broken-01
uv run asset-lookup show slow-01
```

Check each exit code against the table in the README. Then:

- `slow-01` takes 3 seconds, which is within the default 5-second timeout. Set `INVENTORY_TIMEOUT_SECONDS=1` in `.env`, try it again, and note the exit code. Then set it back to `5`;
- set `INVENTORY_API_TOKEN=wrong` in your **shell** (`export ...` in Bash, `$env:INVENTORY_API_TOKEN="wrong"` in PowerShell) and run `show db-03`. Which value won, the shell's or `.env`'s, and why? Unset it afterwards;
- stop the fake server and run `show db-03` once more.

Record the outputs and exit codes in `NOTES.md`.

### Milestone 7: Your own tests (30 min)

Create `tests/unit/` and write **at least 10** test cases with respx (use the `inventory` and `client` fixtures from `conftest.py`). Cover things the acceptance tests don't, for example:

- `429 Too Many Requests`: decide whether that's "unavailable" or an unexpected answer, implement your decision, and test it. Document the choice in `NOTES.md`;
- a page whose `items` isn't a list, or a page that's empty although `total` says there are more;
- `add_note` without a ticket id: what's sent as `ticket_id`?
- a created note whose `id` isn't an integer;
- `load_settings` with spaces and trailing slashes in `INVENTORY_BASE_URL`;
- the client working with `httpx.MockTransport` passed as `transport=`;
- an asset id containing characters such as spaces or `/`: what URL does the client send?

As in Session 04, **prove two of your tests can fail**: break the code they cover, record the failure in `NOTES.md`, and restore it.

### Milestone 8: Security check (10 min)

1. `git status` and `git ls-files`: `.env` must not appear in either. `git check-ignore .env` must print `.env`.
2. Search your source and tests for the real token value: `git grep -n "local-dev-token" -- src tests`. It must print nothing; the fake server and the README may mention it, your code may not.
3. Trigger each error path from Milestone 6 again and read every message: none may contain the token.

### Milestone 9: Quality gate (5 min)

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
```

Commit, and tag the result: `git tag session-05`.

---

## Acceptance criteria

| Check | Expected result |
|---|---|
| `uv run pytest tests/acceptance` | `46 passed` |
| `uv run pytest tests/unit` | At least 10 passed |
| `uv run asset-lookup show db-03` (fake server running) | One line describing the asset; exit code `0` |
| `uv run asset-lookup show nope` | `error: ...` on stderr; exit code `1` |
| `uv run asset-lookup show broken-01`, or any command with the server stopped | `error: ...` on stderr, no traceback; exit code `3` |
| `uv run asset-lookup show db-03` with `INVENTORY_API_TOKEN` empty | `error: INVENTORY_API_TOKEN is not set ...`; exit code `2` |
| `git check-ignore .env` | Prints `.env` |
| `git grep -n "local-dev-token" -- src tests` | No output |
| `git diff starter -- tests/acceptance` | No output |
| `uv run ruff check .` and `uv run ruff format --check .` | Both pass |
| `NOTES.md` | Answers for Milestones 1, 5, 6 and 7, and the reflection |

## Debugging guidance

| You see | Where to look |
|---|---|
| `httpx.ConnectError: ... actively refused` or `Connection refused` when running the CLI | The fake server isn't running, or is on another port. Check `INVENTORY_BASE_URL`. |
| `401` although the token looks right | Is the server reading the same token? It uses `INVENTORY_API_TOKEN` from its own environment or `.env`, defaulting to `local-dev-token`. Restart it after changing `.env`. |
| `RESPX: <Request(...)> not mocked!` in a test | Your client requested a path or method the test didn't expect. Print `request.url` in your client, or compare the path with the route in the test. A trailing slash or a missing leading `/` is a common cause. |
| `test_timeout_is_applied` fails | Pass `timeout=timeout_seconds` when you create the `httpx.Client`, and don't hard-code a number. |
| `test_transport_failures` fails on `__cause__` | Use `raise InventoryUnavailable(...) from error`. |
| `RuntimeError: Cannot send a request, as the client has been closed` in your own code | You used the client after its `with` block ended. |
| The settings test reads a value you didn't set | A real `.env` or shell variable is leaking in. The `clean_env` fixture prevents that; use it in your own settings tests. |
| `list_assets` loops forever | Your stop condition never becomes true. Stop when a page is empty, as well as when you have `total` items. |
| The CLI prints `Z?rich` or `ZÃ¼rich` | Your terminal's encoding, not your code: use Windows Terminal, or set `PYTHONUTF8=1`. |

## Extension challenges (optional)

1. **Retries for reads.** Add an optional `retries` setting that retries `get_asset` and `list_assets` (never `add_note`) after a timeout, a connection error, `502`, `503` or `504`, with exponential backoff. Test it with respx `side_effect` lists, which return different responses on successive calls.
2. **`Retry-After`.** Make a `429` or `503` respect the `Retry-After` header, capped at a maximum wait.
3. **Request logging.** Use HTTPX's event hooks (`event_hooks={"response": [...]}`) to log each request's method, path, status and duration at `DEBUG` level, and write a test that proves the `Authorization` header is never logged.
4. **A health check.** Add `InventoryClient.is_healthy()` using `GET /health` (which needs no token), and an `asset-lookup health` command.

## Reflection

Answer briefly in `NOTES.md`:

1. Which HTTP failure surprised you most, and how does your client present it to a caller?
2. Why does the client raise `AssetNotFound` for a `404`, instead of returning `None`? When would `None` be the better design?
3. You tested mostly with respx and a little against the fake server. What does each kind of test catch that the other doesn't?
4. Compare your client with how you'd build the same thing in your main language. What did HTTPX make easier or harder?

## Deliverables

Submit **one** of the following, as your course instructions specify:

- a link to a Git repository containing the project, with the `session-05` tag (push only to a repository you own; keep it private if you prefer), **or**
- a `.zip` of the project folder **without** `.venv/` and **without `.env`**.

The submission must include:

- [ ] `src/asset_lookup/settings.py` and `client.py` implemented
- [ ] `tests/acceptance/` unchanged, and your `tests/unit/` with at least 10 test cases
- [ ] `.env.example`, but **not** `.env`
- [ ] `NOTES.md` with your milestone answers and the reflection
- [ ] All acceptance criteria passing
