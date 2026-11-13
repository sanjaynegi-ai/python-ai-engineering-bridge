# Session 06 Assignment: Project 02 Begins, Contracts with Pydantic

**Type:** Independent. Complete this without an AI coding assistant; Session 13 covers AI-assisted work.
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb), and the Project 01 checkpoint
**Project:** this starts **Project 02: Python API Service** (`incident-api`), which grows through Sessions 07 and 08.

---

## Business scenario

The nightly incident report from Project 01 is about to become a **service**. In Session 07, other teams will send tickets to it over HTTP and read reports from it. Before that, the team lead wants the data rules in one place, for two reasons:

- Today, the rules for a valid ticket live in about 50 lines of `validate_record`, plus `Ticket.from_record`, plus `load_config`. The HTTP API would need a third copy, and its documentation a fourth.
- Configuration is a `config.json` file with a hand-written loader. Operations wants environment variables, like every other service they run.

You'll rebuild the data layer of the incident report with **Pydantic**: a `Ticket` model that validates **and** normalises, rejections built from `ValidationError`, report models that serialise themselves, and `pydantic-settings` for configuration. The output must stay exactly the same as Project 01's, so that nobody downstream notices the change, apart from clearer error messages.

## Learning objectives

By completing this assignment you will:

- **Define** Pydantic models with required, nullable, constrained, strict and nested fields.
- **Write** field validators that normalise data, and a model validator for a cross-field rule.
- **Map** a `ValidationError` to concise, user-facing problem descriptions.
- **Serialise** a nested report with `model_dump_json`, including an `exclude` option.
- **Load** typed settings from environment variables and `.env` with `pydantic-settings`.
- **Compare** declarative validation with the hand-written version you replaced.

## Prerequisites

- Project 01 complete (or the Project 01 checkpoint, which is in the course repository at `projects/01-python-data-processor/checkpoint/`).
- The Session 06 concepts notebook.

---

## Project setup

Copy the Project 02 starter out of the course repository, adjusting the source path:

```bash
# macOS / Linux / Git Bash
cp -r ~/python-ai-engineering-bridge/projects/02-python-api-service/starter ~/skillup/incident-api

# PowerShell
Copy-Item -Recurse ~\python-ai-engineering-bridge\projects\02-python-api-service\starter ~\skillup\incident-api
```

```bash
cd ~/skillup/incident-api
git init
git add .
git commit -m "Project 02 starter"
git tag starter
uv sync
uv run pytest
```

pytest stops with five collection errors, because the test files import models that don't exist yet. That's expected. Each milestone below has **its own** acceptance test file, which you can run as soon as that milestone is done.

What's provided, and what's yours:

| File | Status |
|---|---|
| `summary.py`, `errors.py`, `cli.py`, `__main__.py` | Provided. `summary.py` is Project 01's, unchanged: it only uses attributes such as `ticket.team`, so it works with Pydantic models as well as dataclasses |
| `loading.py` | `read_export` provided; you write `load_exports` |
| `models.py`, `settings.py`, `report.py` | Yours |
| `tests/acceptance/` | Provided; one file per milestone. Don't edit |

---

## Requirements

| # | Requirement |
|---|---|
| R1 | All 53 acceptance tests pass, unchanged. |
| R2 | `Ticket` validates and normalises raw records by itself. No hand-written type checks remain in the project. |
| R3 | `age_hours` is **strict** (no `"12"`, no `true`), and the other fields keep Pydantic's default lax mode. |
| R4 | Every problem in a record is reported as `field: message`; a problem with the whole record as `record: message`. |
| R5 | `uv run incident-report` produces the same totals, teams, breaches and top tags as Project 01 for the sample data, and exits with `1`. |
| R6 | Settings come from `INCIDENT_*` environment variables or `.env`. Invalid settings produce a clear message and exit code `2`, never a traceback. |
| R7 | At least **10** test cases of your own in `tests/unit/`. |
| R8 | `uv run ruff check .` and `uv run ruff format --check .` pass. |

---

## Implementation milestones

### Milestone 1: Read what you're replacing

Open the Project 01 checkpoint's `loading.py` and `models.py` (or your own Project 01). In `NOTES.md`:

1. Count the lines of `validate_record`, `Ticket.from_record` and `load_config`, including helpers.
2. List every rule they enforce: required fields, types, allowed values, ranges, normalisation, configuration checks.
3. For each rule, predict how it will be expressed in Pydantic: a type, `Field(...)`, `Literal`, a field validator, or a model validator.

Keep the list; you'll tick it off as you go.

### Milestone 2: The `Ticket` model

In `models.py`, write `class Ticket(BaseModel)`:

| Field | Type | Rules |
|---|---|---|
| `id` | `str` | matches `^INC-\d+$` |
| `title` | `str` | at least 1 character |
| `team` | `str` | at least 1 character; stored stripped and lower-case |
| `priority` | the provided `Priority` literal | P1–P4 only |
| `status` | `str` | stored stripped and lower-case |
| `age_hours` | `int` | **strict**; 0 or more |
| `assignee` | `str` or `None` | **required** key; blank or whitespace becomes `None`; stored stripped |
| `tags` | tuple of `str` | required; stored lower-case, unique, sorted |

Also: instances are **frozen**; unknown fields are ignored; keep Project 01's `is_open` property and `is_breached(sla_hours)` method.

Hints:

- `assignee` must be *required* but may be `null`. Re-read "Required, optional, defaulted" in Part 2 of the concepts notebook.
- With a `tuple[str, ...]` type in lax mode, a JSON list is accepted, and a plain string such as `"network"` is rejected. That's the behaviour you want.
- One `@field_validator("team", "status")` can clean both fields.

```bash
uv run pytest tests/acceptance/test_ticket.py
```

25 tests. When they pass, tick off the rules in your Milestone 1 list.

### Milestone 3: Settings

Replace `config.json` with `class Settings(BaseSettings)` in `settings.py`, as its docstring describes:

- the `INCIDENT_` prefix, `.env` support, frozen instances, unknown variables ignored;
- `sla_hours` typed as a dict of `Priority` to `PositiveInt`, so that unknown priorities and non-positive hours are rejected by the types alone;
- a `@model_validator(mode="after")` that rejects `sla_hours` unless it covers P1 to P4 and strictly increases from P1 to P4.

```bash
uv run pytest tests/acceptance/test_settings.py
```

One of these tests sets a variable that isn't valid JSON. Note which exception that raises, and why the provided `cli.py` catches it separately from `ValidationError`. Answer in `NOTES.md`.

### Milestone 4: Rejections and loading

Add `class Rejection(BaseModel)` to `models.py`: frozen; `file: str`; `record: int | None = None`; `id: str | None = None`; `problems: list[str]`.

Then the classmethod `Rejection.from_validation_error(error, *, file, record, raw)`:

- one problem per entry of `error.errors(include_url=False)`, formatted `field: message`, with the location's parts joined by dots (`tags.1`), and `record` when the location is empty;
- `id` taken from `raw` only if `raw` is a dict whose `"id"` is a string.

Then write `load_exports(paths)` in `loading.py`. It's Project 01's version without the hand validation: call `Ticket.model_validate(record)` and catch `ValidationError`. It no longer needs `sla_hours`, because the model knows the priorities.

```bash
uv run pytest tests/acceptance/test_rejection_and_loading.py
```

### Milestone 5: Report models

Add the report models to `models.py`. Their field names are exactly the keys of Project 01's report:

- `Totals`: `valid_records`, `unique_tickets`, `open`, `breached`, `rejected` (all `int`);
- `TeamStats`: `open`, `breached`, `unassigned_open` (`int`), `oldest_open_hours` (`int | None`);
- `Breach`: `id`, `title`, `team`, `priority`, `age_hours`, `sla_hours`;
- `TagCount`: `tag`, `count`;
- `Report`: `generated_at` (`datetime`), `totals`, `teams` (dict of team to `TeamStats`), `breaches`, `top_tags`, `rejected` (list of `Rejection`).

Then implement `build_report` and `write_report` in `report.py`:

- `build_report` is Project 01's logic, building models instead of dicts. `TeamStats(**stats)` turns each of `team_summary`'s dicts into a model. `ticket.model_dump(include={...})` is handy for `Breach`.
- Drop the microseconds from `generated_at` (`.replace(microsecond=0)`).
- `write_report` is now short: `model_dump_json(indent=2)`, with `exclude={"rejected"}` when `include_rejected` is false. Write it as UTF-8, with a final newline.

```bash
uv run pytest tests/acceptance/test_report.py
```

### Milestone 6: Run it

```bash
uv run pytest                          # all 53 acceptance tests
uv run incident-report
uv run incident-report --summary-only
```

Compare `out/report.json` with Project 01's output. The numbers must match. Then break the settings, one at a time:

```bash
# Bash
INCIDENT_SLA_HOURS='{"P1": 30, "P2": 24, "P3": 72, "P4": 168}' uv run incident-report
INCIDENT_SLA_HOURS='P1=4' uv run incident-report

# PowerShell
$env:INCIDENT_SLA_HOURS='{"P1": 30, "P2": 24, "P3": 72, "P4": 168}'; uv run incident-report
$env:INCIDENT_SLA_HOURS='P1=4'; uv run incident-report
Remove-Item Env:INCIDENT_SLA_HOURS
```

Both should exit with `2` and a readable message. Record the outputs in `NOTES.md`.

### Milestone 7: Your own tests

Create `tests/unit/` and write at least **10** test cases. Ideas:

- a record parsed with `Ticket.model_validate_json(...)` from a JSON string;
- an empty tag list; tags in mixed case with duplicates;
- a numeric `id` such as `3004`: rejected or converted? Why?
- a record with **four** problems produces four problem strings;
- `Rejection.from_validation_error` when `raw` has a non-string `id`;
- `Settings` with `INCIDENT_SLA_HOURS` covering P1–P4 but with equal values;
- the report's JSON read back with `Report.model_validate_json` equals the original.

As before, prove that two of your tests can fail, and record the failures in `NOTES.md`.

### Milestone 8: Measure the change

In `NOTES.md`, compare with Milestone 1:

1. How many lines do `Ticket`, `Rejection` and `Settings` take, together, compared with the code they replaced?
2. Which rules became **declarations** (types, `Field`, `Literal`), and which still needed **code** (validators)?
3. How did the rejection messages change? Pick one rejected record and compare the Project 01 message with the new one. Which is better for the data owner, and why?

### Milestone 9: Quality gate

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
git add .
git commit -m "Session 06: Pydantic models and settings"
git tag session-06
```

---

## Acceptance criteria

| Check | Expected result |
|---|---|
| `uv run pytest tests/acceptance` | `53 passed` |
| `uv run pytest tests/unit` | At least 10 passed |
| `uv run incident-report` | Same totals, teams, breaches and top tags as Project 01; exit code `1` |
| `uv run incident-report --summary-only` | `out/report.json` has no `"rejected"` key; `totals.rejected` is still `6` |
| An invalid `INCIDENT_SLA_HOURS` (rule-breaking, or not JSON) | A readable message on stderr, no traceback; exit code `2` |
| `git grep -n "isinstance" -- src` | No hand-written type checks left in your code. (`read_export`'s list check and `from_validation_error`'s `id` check are fine) |
| `git diff starter -- tests/acceptance` | No output |
| `uv run ruff check .` and `uv run ruff format --check .` | Both pass |
| `NOTES.md` | Milestones 1, 3, 6, 7 and 8, and the reflection |

## Debugging guidance

| You see | Where to look |
|---|---|
| `ImportError: cannot import name 'Rejection' from 'incident_api.models'` | You haven't reached that milestone yet. Run only the current milestone's test file. |
| `test_assignee` or a "required" test fails | `assignee: str \| None = None` makes it optional. The key must be required: no default. |
| `"12"` or `true` accepted as `age_hours` | `Field(strict=True, ge=0)` on that field. |
| A cleaned field is `None` | Your validator doesn't `return` the value. |
| `test_unknown_fields_are_ignored` fails | Don't set `extra="forbid"` on `Ticket`: other teams' exports may gain fields. |
| `tags` stays a list, or isn't sorted | Return `tuple(sorted({...}))` from the tags validator. |
| `Settings` reads values you didn't set | A real `.env` or `INCIDENT_*` variable leaks in. The tests use the `clean_env` fixture; use it in yours. |
| The JSON has `"2026-10-21T02:00:00.123456Z"` | Drop the microseconds in `build_report`. |
| `TypeError: Object of type Ticket is not JSON serializable` | You're mixing `json.dumps` with models. Use `report.model_dump_json(...)`. |
| A traceback from `Settings()` | The provided `cli.py` catches both `SettingsError` and `ValidationError`. If you changed it, compare with the starter. |

## Extension challenges (optional)

1. **Strict everywhere?** Make the whole `Ticket` model strict with `ConfigDict(strict=True)`. Which acceptance tests fail, and why? (Hint: tuples.) Find the smallest change that keeps strictness and passes.
2. **A camelCase export.** A new partner sends `ageHours`, `assignedTo` and `createdAt`. Add aliases, so the same `Ticket` accepts both formats, and write tests for both.
3. **`SecretStr` in settings.** Add an optional `INCIDENT_WEBHOOK_TOKEN` setting as `SecretStr | None`, and prove with a test that it never appears in `repr(settings)` or in the CLI's output. Session 08 will use a token like this.
4. **JSON Schema.** Print `Ticket.model_json_schema()` and compare it with your Milestone 1 list. Session 07's API documentation is generated from exactly this.

## Reflection

Answer briefly in `NOTES.md`:

1. Which rule was hardest to express declaratively, and why?
2. When would you still write validation by hand rather than with Pydantic?
3. The `Ticket` model now validates and normalises. Is it a problem that an invalid `Ticket` can no longer exist? When might you want to represent "invalid but kept" data?
4. How does this compare with validation in your main language (Bean Validation, DataAnnotations, zod)?

## Deliverables

Submit **one** of the following, as your course instructions specify:

- a link to a Git repository containing the project, with the `session-06` tag (push only to a repository you own; keep it private if you prefer), **or**
- a `.zip` of the project folder **without** `.venv/`, `out/` and `.env`.

The submission must include:

- [ ] `models.py`, `settings.py`, `report.py` and `load_exports` implemented
- [ ] `tests/acceptance/` unchanged, and your `tests/unit/` with at least 10 test cases
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
