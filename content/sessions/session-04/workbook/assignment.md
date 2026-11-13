# Session 04 Assignment: Project 01, the `incident-report` Package

**Type:** Independent. Complete this without an AI coding assistant; Session 13 covers AI-assisted work.
**Estimated time:** 2.5–3 hours
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb), [`03-debugging-lab.ipynb`](../notebooks/03-debugging-lab.ipynb), and your Session 02 and 03 workbooks
**Milestone:** this completes **Project 01: Python Data Processor**, the first course checkpoint.

---

## Business scenario

The nightly incident report is now relied on by the whole Orbital Logistics (fictional) on-call rota, and a second engineer is joining you to maintain it. Before they start, the team lead asks for three things:

1. **A real package**, installable with one command, with each responsibility in its own module, so two people can work on it without tripping over each other.
2. **Typed domain objects** instead of dicts with string keys, so a typo like `ticket["teams"]` fails in the editor, not at 02:00.
3. **A proper test suite** that runs with one command in CI, replacing the hand-written checker scripts.

You'll restructure your Session 02 and 03 code into the `incident_report` package. The behaviour stays the same; the structure changes completely. A starter project provides the layout, the configuration and 48 acceptance tests. You move your code in, then write your own unit tests.

## Learning objectives

By completing this assignment you will:

- **Refactor** working code into a `src/`-layout package with one responsibility per module and imports that point one way.
- **Model** tickets, rejections and configuration as frozen dataclasses, with a `@classmethod` constructor and a `@property`.
- **Run** a package as a command (`[project.scripts]`) and as a module (`python -m`).
- **Write** pytest unit tests with fixtures, `tmp_path`, `parametrize` and `pytest.raises`, and **prove** that each test can fail.
- **Configure** Ruff for a project, and keep the code lint-clean.
- **Debug** with `breakpoint()`, `pytest --pdb` and the VS Code debugger.

## Prerequisites

- Your Session 02 `ticket_summary.py` and Session 03 `incident_report.py`, both passing their checkers. You'll move that code; you won't rewrite it from scratch.
- The Session 04 concepts notebook and debugging lab.
- VS Code with the Python extension, for Milestone 8.

---

## Project setup

Copy the **starter project** from the course repository into a new folder outside it. Adjust the path to wherever you cloned the course:

```bash
# macOS / Linux / Git Bash
cp -r ~/python-ai-engineering-bridge/projects/01-python-data-processor/starter ~/skillup/incident-report

# PowerShell
Copy-Item -Recurse ~\python-ai-engineering-bridge\projects\01-python-data-processor\starter ~\skillup\incident-report
```

Then:

```bash
cd ~/skillup/incident-report
git init
git add .
git commit -m "Project 01 starter"
git tag starter
uv sync
```

`uv sync` creates `.venv/`, installs pytest and Ruff, and installs `incident_report` itself in editable mode. Now run the tests:

```bash
uv run pytest
```

You should see three `ERROR tests/acceptance/...` lines, each caused by `ImportError: cannot import name 'Config' from 'incident_report.models'`, ending with `Interrupted: 3 errors during collection`. That's expected: `models.py` is empty until Milestone 2, and pytest stops when test files can't even be imported.

The full layout is described in the starter's `README.md`. Read it now.

---

## Requirements

| # | Requirement |
|---|---|
| R1 | All 48 acceptance tests in `tests/acceptance/` pass, unchanged. |
| R2 | `Ticket`, `Rejection` and `Config` are **frozen dataclasses** with the fields described in `models.py`. `Ticket.tags` and `Rejection.problems` are tuples. |
| R3 | Modules import each other only in the direction shown in the concepts notebook's import diagram. `models` imports nothing from the package. No circular imports. |
| R4 | `uv run incident-report`, `uv run python -m incident_report` and `uv run incident-report config.json` all produce the Session 03 report and exit code `1` for the sample data. |
| R5 | You add **at least 12 test cases** in `tests/unit/`, using at least one `parametrize`, one fixture from `conftest.py`, `tmp_path`, and `pytest.raises`. |
| R6 | For at least two of your unit tests, you've shown in `NOTES.md` that they **fail** when the code is broken. |
| R7 | `uv run ruff check .` and `uv run ruff format --check .` pass with the project's configuration. |
| R8 | No `breakpoint()` calls, print-debugging or commented-out code left behind. |

R3 is easy to state and easy to break. Here is the intended import graph:

```text
cli ──► loading ──► models
 │        └──────► errors
 ├──► report ──► summary ──► models
 │        └────────────────► models
 └──► errors
```

---

## Implementation milestones

Run `uv run pytest` after every milestone; the number of passing tests should go up each time. To run one file, `uv run pytest tests/acceptance/test_models.py`. To see each test's name, add `-v`.

### Milestone 1: Read the project (15 min)

1. Open `pyproject.toml`. Find the line that creates the `incident-report` command, the Ruff rule selection, and the pytest settings. In `NOTES.md`, explain what `--import-mode=importlib` is for. (The concepts notebook's common-mistakes table has the answer.)
2. Open `tests/conftest.py`. What does the `make_record` fixture return, and why is it a function rather than a dict? (Hint: Lab 5 of the debugging lab.)
3. Open `tests/acceptance/test_models.py`. These tests are your **specification** for Milestone 2. Read every one before you write any code.

### Milestone 2: `models.py` (30 min)

Write the three dataclasses described in the module docstring.

- `@dataclass(frozen=True)` on each. Field **order** matters: the tests build `Ticket` with keyword arguments, but `test_config_fields` checks `Config`'s order.
- `Ticket.from_record` is your Session 02 `normalise_ticket`, turned into a `@classmethod` that returns `cls(...)`. One difference: `tags` must be a **tuple**, so `tuple(sorted(...))`.
- `is_open` is a `@property`, so callers write `ticket.is_open` with no parentheses. `is_breached` is an ordinary method, because it needs the SLA table.
- `Rejection.to_dict()` returns a plain dict for the JSON report, with `problems` as a list.
- Keep `CLOSED_STATUSES` where it is.

```bash
uv run pytest tests/acceptance/test_models.py -v
```

All 13 should pass. Then run the full suite: the collection errors are gone, and the other tests now fail with `NotImplementedError` instead.

In `NOTES.md`: why does `Ticket` store tags as a tuple rather than a list? Give two reasons, one from Session 02 and one from today.

### Milestone 3: `loading.py` (25 min)

Move `load_config`, `read_export`, `validate_ticket` and `load_exports` from your Session 03 `incident_report.py`, and move `ConfigError`/`ExportError` usage to the provided `errors.py`. Then adapt them:

- `load_config` returns `Config(input_dir=..., output_file=..., sla_hours=...)` instead of a dict.
- `validate_ticket` is renamed `validate_record`: it checks *raw records*, before they become tickets. Same messages, same order.
- `load_exports` returns `Ticket` objects (via `Ticket.from_record`) and `Rejection` objects (with `problems` as a tuple), instead of dicts.

```bash
uv run pytest tests/acceptance/test_loading.py
```

### Milestone 4: `summary.py` (20 min)

Move `deduplicate`, `team_summary` and `top_tags` from your Session 02 `ticket_summary.py`, and change dict access to attribute access: `ticket["team"]` becomes `ticket.team`. Your editor now autocompletes the field names, which is the point.

Add `breaches(tickets, sla_hours)`: open, breached tickets, oldest first. In Session 03 that logic lived inside `build_report`. Why is it better as its own function? (Think about testing.)

Your Session 02 `is_open` and `is_breached` functions are gone: those rules now live on `Ticket`. Watch out for `ticket.is_open()`, which fails with `TypeError: 'bool' object is not callable`. It's a property, so there are no parentheses.

### Milestone 5: `report.py` (15 min)

Move `build_report` and `write_report`. `build_report` receives `Ticket`s that are already normalised, so it only needs to deduplicate. Use `breaches()` from `summary`, and `rejection.to_dict()` for the `"rejected"` list. The report's shape and values are exactly those of Session 03.

### Milestone 6: `cli.py` (15 min)

Move `main`. It now uses `config.input_dir` instead of `config["input_dir"]`, and `rejection.problems` instead of `entry["problems"]`. Then run the whole thing three ways:

```bash
uv run incident-report
uv run python -m incident_report
uv run incident-report missing.json
```

The first two print the Session 03 summary and exit with `1`; the third exits with `2`. Then run the full suite: **48 passed**. Commit.

Look at what you didn't have to write: no `if __name__ == "__main__":` in `cli.py`. Where does that responsibility live now? Answer in `NOTES.md`.

### Milestone 7: Your own unit tests (40 min)

The acceptance tests check the agreed behaviour. Your unit tests pin down the **edge cases** that matter to you as the maintainer. Create `tests/unit/` with files such as `test_models.py`, `test_loading.py` and `test_summary.py`.

Write at least 12 test cases (each `parametrize` row counts as one), covering at least six of these:

- assignee normalisation: `None`, `""`, `"   "`, `" amira "`;
- tags in mixed case with duplicates; an empty tag list;
- `Ticket.is_breached` with a priority missing from the SLA table;
- an export file containing `[]`; an empty file; a file with a non-object record;
- `deduplicate` of an empty list, and that it doesn't change its input;
- `breaches` when nothing is late;
- `team_summary` counting only *open* unassigned tickets;
- `top_tags` with fewer tags than requested, and with no tags at all;
- `write_report` into a folder that doesn't exist yet.

Rules of thumb: one behaviour per test; arrange, act, assert; a descriptive name; fresh data from fixtures, never module-level lists that tests modify.

**Prove your tests work.** Pick two of them. For each, break the code they test (for example, change `>` to `>=`, or `return assignee or None` to `return assignee`), run the tests, copy the failure output into `NOTES.md`, then restore the code. A test you have never seen fail hasn't shown you that it can.

```bash
uv run pytest tests/unit -v
```

### Milestone 8: Debug with breakpoints (15 min)

1. In `summary.py`, add `breakpoint()` as the first line of `team_summary`. Run:

   ```bash
   uv run pytest tests/acceptance/test_summary_and_report.py -k team_summary_sample -s
   ```

   At the `(Pdb)` prompt: `p len(tickets)`, `n` twice, `p open_by_team`, `w`, then `c`. In `NOTES.md`, write what `w` showed you, and how it relates to a traceback.
2. Remove the `breakpoint()`. In VS Code, select the project's `.venv` interpreter, set a gutter breakpoint on the same line, and run the same test with **Debug Test** from the Testing view. Inspect a `Ticket` in the Variables panel.
3. Temporarily break one assertion in one of your unit tests and run `uv run pytest tests/unit --pdb`. pytest stops at the failure. Inspect the values with `p`, quit with `q`, and restore the test.

### Milestone 9: Quality gate and checkpoint (10 min)

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
```

The project's Ruff rules are stricter than the defaults you've used so far: `B`, `UP` and `SIM` are switched on. Fix what they report; `uv run ruff check --fix .` handles the safe fixes. Then commit, and mark the checkpoint:

```bash
git add .
git commit -m "Project 01 complete"
git tag project-01
```

---

## Acceptance criteria

| Command | Expected result |
|---|---|
| `uv run pytest tests/acceptance` | `48 passed` |
| `uv run pytest tests/unit` | At least 12 passed |
| `uv run pytest` | Everything passes, no warnings |
| `uv run incident-report` | The Session 03 summary; `out/report.json` written; exit code `1` |
| `uv run python -m incident_report` | The same |
| `uv run incident-report missing.json` | One `error:` line on stderr; exit code `2` |
| `uv run ruff check .` | `All checks passed!` |
| `uv run ruff format --check .` | Every file already formatted |
| `git diff starter -- tests/acceptance` | No output: the provided tests are unchanged since the starter commit |
| `NOTES.md` | Answers for Milestones 1, 2, 6 and 8, the two failing-test proofs (M7), and the reflection |

## Testing

- `uv run pytest -x` stops at the first failure, which is useful while moving code.
- `uv run pytest -k breach` runs only tests whose names contain `breach`.
- `uv run pytest --lf` re-runs only the tests that failed last time.
- A failing `assert` shows both values. For long dicts, pytest prints a diff; read it from the first `-`/`+` line.
- **`E` in the progress line**, rather than `F`, means a fixture failed before the test ran. Read the "ERROR at setup" section.

## Debugging guidance

| You see | Where to look |
|---|---|
| `ImportError: cannot import name 'Ticket' from 'incident_report.models'` during collection | `models.py` doesn't define it yet, or has a typo in the class name. Collection errors stop every test, so fix these first. |
| `ModuleNotFoundError: No module named 'incident_report'` | You're not using the project environment, or haven't run `uv sync`. Use `uv run`, and in VS Code select `.venv`. |
| `ImportError: ... partially initialized module ... (most likely due to a circular import)` | Two modules import each other. Check against the import graph in R3; usually something imported into `loading` or `models` belongs in `cli`. |
| `TypeError: 'bool' object is not callable` | `ticket.is_open()`: it's a property, so drop the parentheses. |
| `dataclasses.FrozenInstanceError: cannot assign to field` | You're modifying a ticket after creating it. Compute everything first, then call `cls(...)` once, or use `dataclasses.replace()`. |
| `AttributeError: 'dict' object has no attribute 'team'` | Raw dicts are reaching code that expects `Ticket`s. `load_exports` must convert valid records with `Ticket.from_record`. |
| `assert Ticket(... tags=['network', 'vpn']) == Ticket(... tags=('network', 'vpn'))` | Tags must be a tuple: `tuple(sorted(...))`. |
| `TypeError: Object of type Rejection is not JSON serializable` | Use `rejection.to_dict()` in the report, not the dataclass itself. |
| `import file mismatch` | Two test files share a name and `--import-mode=importlib` was removed from `pyproject.toml`. Put it back. |
| A test passes alone but fails in the full run | Shared mutable data between tests. See Lab 5. |

## Extension challenges (optional)

1. **Coverage.** Add `pytest-cov` as a dev dependency (`uv add --dev pytest-cov`) and run `uv run pytest --cov=incident_report --cov-report=term-missing`. Which lines are never executed by any test? Add tests for the ones that matter, and explain in `NOTES.md` why 100% is not the goal.
2. **A `Report` dataclass.** Replace the dict returned by `build_report` with a frozen `Report` dataclass, and convert it to JSON only in `write_report`. What changes in the tests, and is it worth it?
3. **Type checking.** Run `uvx pyright src` (or `uvx mypy src`). Fix what it reports, and note which problems Ruff and the tests had missed.
4. **Continuous integration.** Write a `.github/workflows/ci.yml` that runs `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .` and `uv run pytest` on every push. Don't push it anywhere you haven't been asked to; just make sure the commands would work in a clean clone (Session 01, Milestone 6).

## Reflection

Answer briefly in `NOTES.md`:

1. Which module boundary was hardest to decide, and why?
2. Compare dataclasses with dicts for tickets: what did you gain, what did you lose, and where would you still use a dict?
3. The acceptance tests and your unit tests overlap in places. What's each kind for, and who is each one written for?
4. How does this package compare with how you'd structure the same tool in Java, C# or TypeScript?

## Deliverables

Submit **one** of the following, as your course instructions specify:

- a link to a Git repository containing the project, with the `project-01` tag (push only to a repository you own; keep it private if you prefer), **or**
- a `.zip` of the project folder **without** `.venv/` and `out/`.

The submission must include:

- [ ] The complete package in `src/incident_report/`
- [ ] `tests/acceptance/` unchanged, and your `tests/unit/` with at least 12 test cases
- [ ] `pyproject.toml` and `uv.lock`
- [ ] `NOTES.md` with your milestone answers, the failing-test proofs and the reflection
- [ ] All acceptance criteria passing
