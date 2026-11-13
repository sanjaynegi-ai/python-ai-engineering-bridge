# Session 03 Assignment: The Nightly Incident Report

**Type:** Independent. Complete this without an AI coding assistant; Session 13 covers AI-assisted work.
**Estimated time:** 2–2.5 hours
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb), and your Session 02 workbook

---

## Business scenario

Your Session 02 summary worked on data already in memory. Now it has to run unattended every night at Orbital Logistics (fictional) against the real export folder, and the real folder is not tidy:

- One file was cut off halfway through an upload, so it isn't valid JSON.
- One file came from the old helpdesk system, which wraps its tickets in an object instead of a list.
- Some records have a missing ID, an age of `"12"` (a string) or `true`, an unknown priority, or tags that aren't a list.
- One file contains non-ASCII text (`Zürich`), which breaks on machines that don't read files as UTF-8.

The on-call lead's requirements are simple: **one bad file or record must never stop the report**, every rejection must be listed so the data owner can fix it, and the exit code must tell the scheduler whether anything was rejected.

You'll build `incident_report.py`: configuration loading, safe reading, hand validation, a JSON report, and a command-line entry point with meaningful exit codes. This becomes the core of **Project 01** in Session 04.

## Learning objectives

By completing this assignment you will:

- **Design** functions with keyword-only options and no mutable defaults.
- **Raise** your own exception types, **chain** them to the original error, and **handle** them in the one place that knows what to do.
- **Read** and **write** files safely with `pathlib`, `with` and explicit UTF-8 encoding.
- **Parse**, **validate** and **serialise** JSON, collecting every problem instead of stopping at the first.
- **Interpret** a chained, multi-frame traceback from your own code.
- **Return** exit codes and error messages that a scheduler and a human can both act on.

## Prerequisites

- The Session 02 workbook completed: your `ticket_summary.py` passes all 16 checks.
- The Session 03 concepts notebook worked through, especially Parts 5–7.
- The course repository cloned, so you can copy the starter files.

---

## Project setup

Create a new project outside the course repository:

```bash
uv init --no-package --python 3.13 incident-report
cd incident-report
uv add --dev ruff
```

Delete the generated `main.py`. Then copy in:

1. **The Session 03 starter files**, including the `data/` folder. Adjust the path to where you cloned the course:

   ```bash
   # macOS / Linux / Git Bash
   cp -r ~/python-ai-engineering-bridge/sessions/session-03/workbook/starter/. .

   # PowerShell
   Copy-Item -Recurse ~\python-ai-engineering-bridge\sessions\session-03\workbook\starter\* .
   ```

2. **Your own Session 02 files**, `ticket_summary.py` and `sample_tickets.py`, from your `ticket-summary` project. `incident_report.py` imports your functions from there.

You should now have:

```text
incident-report/
├── check_report.py        ← provided, don't edit
├── config.json            ← provided; you may read it, but the checker doesn't use it
├── data/
│   └── exports/           ← provided synthetic exports, don't edit
│       ├── README.txt
│       ├── tickets-2026-10-19.json
│       ├── tickets-2026-10-20.json
│       ├── tickets-2026-10-21.json
│       └── tickets-legacy.json
├── incident_report.py     ← your work
├── sample_tickets.py      ← yours, from Session 02
├── ticket_summary.py      ← yours, from Session 02
├── pyproject.toml, uv.lock, .python-version, .gitignore, README.md
└── NOTES.md               ← you create this
```

Run the checker:

```bash
uv run check_report.py
```

Expect 22 `TODO` lines and `Passed: 0  Failed: 0  Not implemented: 22`. If you see `ImportError` instead, your `ticket_summary.py` is missing or doesn't define one of the functions listed at the top of `incident_report.py`.

Commit now (`git add .` then `git commit -m "Starter"`), so you can always see what you've changed.

---

## Requirements

| # | Requirement |
|---|---|
| R1 | Every function in `incident_report.py` behaves as its docstring describes, and all 22 checks in `check_report.py` pass. |
| R2 | Low-level errors (`FileNotFoundError`, `UnicodeDecodeError`, `JSONDecodeError`) are translated into `ConfigError` or `ExportError`, **chained** with `from`. |
| R3 | A bad export file becomes one rejected entry; processing continues with the next file. |
| R4 | Every problem in a record is reported, not just the first. Booleans are not accepted as integers. |
| R5 | All files are read and written with `encoding="utf-8"`. The report keeps non-ASCII text readable. |
| R6 | `uv run incident_report.py` writes `out/report.json` with the shape below, lists rejections on **stderr**, and exits with `1` for the sample data. |
| R7 | A configuration problem prints one clear line to stderr, **no traceback**, and exits with `2`. |
| R8 | No function has a mutable default argument, and no function modifies its inputs. |
| R9 | `uv run ruff check .` and `uv run ruff format --check .` both pass. |

### The report

`build_report` returns a dict that `write_report` saves as JSON. For the sample data, with `generated_at` set to 02:00 UTC on 21 October 2026, it looks like this (lists shortened with `...`):

```json
{
  "generated_at": "2026-10-21T02:00:00+00:00",
  "totals": {
    "valid_records": 11,
    "unique_tickets": 10,
    "open": 9,
    "breached": 6,
    "rejected": 6
  },
  "teams": {
    "platform": {"open": 2, "breached": 2, "unassigned_open": 1, "oldest_open_hours": 26},
    "...": "one entry per team, from your Session 02 team_summary"
  },
  "breaches": [
    {
      "id": "INC-3007",
      "title": "Label printer queue stuck in warehouse 4",
      "team": "it-support",
      "priority": "P4",
      "age_hours": 200,
      "sla_hours": 168
    },
    "... every breached open ticket, oldest first, including INC-3009 at the Zürich depot"
  ],
  "top_tags": [
    {"tag": "latency", "count": 3},
    {"tag": "network", "count": 3},
    {"tag": "api", "count": 2}
  ],
  "rejected": [
    {"file": "tickets-2026-10-20.json", "record": 2, "id": null, "problems": ["missing field 'id'"]},
    "... exactly the list load_exports returned"
  ]
}
```

How each part is computed:

- `valid_records`: the number of records `load_exports` accepted, before any cleaning.
- Everything else is computed after cleaning: **normalise every record, then deduplicate**, using your Session 02 functions. `unique_tickets`, `open`, `breached`, `teams` and `breaches` all come from those unique tickets.
- `top_tags`: your `top_tags(open_tickets, 3)`, turned into small dicts. Why not leave them as tuples? Check Part 7 of the concepts notebook.
- `generated_at`: `generated_at.isoformat(timespec="seconds")`.

---

## Implementation milestones

### Milestone 1: Read the contract (10 min)

1. Read every docstring in `incident_report.py`, and the exit codes at the top. Together they're the specification.
2. Open each file in `data/exports/` in your editor. Find, by eye, at least five problems the code will have to handle. Note them in `NOTES.md`, then compare your list with what your finished program reports.
3. Look at the function signatures. Which parameters are keyword-only? Why would `load_exports(paths, sla_hours=...)` be clearer at the call site than `load_exports(paths, SLA)`?

### Milestone 2: `load_config` (25 min)

Run `uv run check_report.py` after each step; the first four checks are about this function.

1. Open the file with `with open(path, encoding="utf-8") as file:` and `json.load(file)`.
2. Catch `FileNotFoundError` and `json.JSONDecodeError` **separately**, and raise `ConfigError(...) from error` for each, with a message that includes the file name.
3. After parsing (outside the `try`), check: it's a dict; it has all three keys; the two paths are strings; `sla_hours` is a dict whose values are positive integers. Remember that `True` is an `int`.
4. Resolve the paths relative to **the config file's folder**: `path.parent / raw["input_dir"]`.

In `NOTES.md`: why resolve paths relative to the config file, rather than to the folder you happen to run the command from? What would break in a scheduled job if you didn't?

### Milestone 3: `read_export` (20 min)

The quiz's Q8 practised this pattern. The differences here are `UnicodeDecodeError`, and that the message must include the line number from the `JSONDecodeError` (`error.lineno`).

Keep the `try` block small: only the open-and-parse step. The shape check comes after it.

### Milestone 4: `validate_ticket` (30 min)

This is the most detailed function. Build it up one check at a time:

1. Not a dict? Return the single message immediately.
2. Loop over `FIELD_TYPES.items()`. Missing field → message, then `continue` to the next field.
3. Wrong type → message. `isinstance(value, expected)` accepts a tuple of types, which is how `assignee` allows `str` **or** `None`. Booleans must be rejected **before** the `isinstance` check, since `isinstance(True, int)` is `True`.
4. The type names in messages: `str`, `int`, `list`, and `"str or None"` for the tuple. `type(None).__name__` is `'NoneType'`, so you'll need to special-case it. A small helper function that turns `expected` into that text keeps the loop readable.
5. After the loop, the three value checks, each only when the field has the right type: `age_hours` not negative, `priority` in `sla_hours`, every tag a string. `all(...)` with a generator expression is handy for the last one.

The checker compares **exact** lists of messages, so copy the formats from the docstring carefully.

### Milestone 5: `load_exports` (20 min)

Loop over the paths. For each one:

- `try` to `read_export` it. On `ExportError`, append **one** rejected entry (`"record": None`, `"id": None`, the error message as its single problem), then `continue`.
- Otherwise `enumerate` the records, validate each, and put it in either `valid` or `rejected`.
- A rejected record's `"id"` is its `"id"` value if the record is a dict and has one, otherwise `None`.

Return the tuple `(valid, rejected)`.

### Milestone 6: `build_report` and `write_report` (25 min)

- Follow "How each part is computed" above. Your Session 02 functions do most of the work.
- `write_report`: `path.parent.mkdir(parents=True, exist_ok=True)`, then open the file with `"w"` and `encoding="utf-8"`, and `json.dump(report, file, indent=2, ensure_ascii=False)`. End the file with a newline.

Check that the report survives a round trip: `json.loads(json.dumps(report)) == report` should be `True`. If it isn't, something in it isn't a JSON type, such as a tuple or a datetime.

### Milestone 7: `main` (20 min)

1. `argv` defaults to `None`. When it's `None`, use `sys.argv[1:]`. Why not `argv=sys.argv[1:]` as the default? (Part 2 of the concepts notebook has the answer, and so does testing: the checker calls `main([...])` directly.)
2. Load the config. On `ConfigError`, print `error: <message>` to **stderr** (`print(..., file=sys.stderr)`) and return `2`.
3. Find the exports with `sorted(config["input_dir"].glob("*.json"))`. Sorting makes the order, and therefore the report, the same on every machine. No files at all? Print an error to stderr and return `2`.
4. Load, build (with `generated_at=datetime.now().astimezone()`, the current time with your time zone), and write the report.
5. Print a one-line summary to stdout, each rejection to stderr, and return `1` if anything was rejected, otherwise `0`.

Run it for real:

```bash
uv run incident_report.py
```

You should see something like this. Your report path will use `\` on Windows:

```text
  rejected tickets-2026-10-20.json[2]: missing field 'id'
  rejected tickets-2026-10-20.json[3]: field 'age_hours' must be int, got str
  rejected tickets-2026-10-20.json[4]: field 'tags' must be list, got str; unknown priority 'P9'
  rejected tickets-2026-10-20.json[5]: field 'age_hours' must be int, got bool
  rejected file tickets-2026-10-21.json: invalid JSON at line 21, column 5: Expecting property name enclosed in double quotes
  rejected file tickets-legacy.json: expected a list of tickets, got dict
Read 4 export files: 11 valid records, 10 unique tickets, 6 rejected
Report written to out/report.json
```

Check the exit code (`echo $?` in Bash, `$LASTEXITCODE` in PowerShell): it should be `1`. Then try `uv run incident_report.py missing.json`: one line on stderr, exit code `2`, no traceback.

Add `out/` to `.gitignore`. It's generated output, like `.venv/`.

### Milestone 8: Read a chained traceback (10 min)

1. In `load_exports`, temporarily change `except ExportError` to `except KeyError`, so export errors are no longer handled.
2. Run `uv run incident_report.py` and copy the full traceback into `NOTES.md`.
3. Annotate it: mark the line that says one exception caused another; the frame where the **original** error was raised; the frame where **your** code raised `ExportError`; and the first frame of yours that the error passed through without being handled.
4. Explain in two sentences why `from error` made this traceback more useful than it would have been without it.
5. Restore `except ExportError`, and confirm the checker passes again.

### Milestone 9: Quality gate (5 min)

```bash
uv run ruff format .
uv run ruff check .
uv run ruff format --check .
uv run check_report.py
```

---

## Acceptance criteria

| Command | Expected result |
|---|---|
| `uv run check_report.py` | `Passed: 22  Failed: 0  Not implemented: 0`, exit code `0` |
| `uv run incident_report.py` | Rejections on stderr, summary on stdout, `out/report.json` written, exit code `1` |
| `uv run incident_report.py missing.json` | One `error:` line on stderr, no traceback, exit code `2` |
| `out/report.json` | Matches the shape above; the `INC-3009` breach title reads `Zürich`, not `Zürich` |
| `uv run ruff check .` | `All checks passed!` |
| `uv run ruff format --check .` | Every file already formatted |
| `git diff --stat check_report.py data/` | No changes to provided files |
| `NOTES.md` | Milestone 1 and 2 answers, the annotated traceback (M8), and the reflection |

## Testing

`check_report.py` copies the sample data into a temporary folder for every check, so it never touches your `config.json`, `data/` or `out/`. When a check fails:

- **"no ExportError was raised"** or **"cause was nothing"**: look at that function's `except` clauses and its `raise ... from error`.
- **A list of messages differs**: compare the two lists element by element; usually one word or the order is off.
- **A crash inside your code**: the message ends with `(at file:line)`. Reproduce it in an interactive session:

  ```bash
  uv run python -i incident_report.py
  ```

  ```python
  >>> validate_ticket({"id": "INC-1", "age_hours": True}, sla_hours={"P1": 4})
  ```

## Debugging guidance

| You see | Where to look |
|---|---|
| `ImportError: cannot import name 'team_summary' from 'ticket_summary'` | Your Session 02 file is missing that function, or you copied the starter's version instead of your finished one. |
| "read_export reads UTF-8" fails with `ZÃ¼rich` | `open()` without `encoding="utf-8"` uses the Windows default (cp1252). On macOS and Linux the default is usually UTF-8, so the checker can't catch this there. Add the encoding anyway. |
| `TypeError: Object of type datetime is not JSON serializable` | Store `generated_at.isoformat(timespec="seconds")`, not the `datetime` itself. |
| `TypeError: 'type' object is not subscriptable`, or a strange error from `isinstance` | Check that you pass the type or tuple from `FIELD_TYPES`, not a string such as `"int"`. |
| A message says `str or NoneType` | `type(None).__name__` is `'NoneType'`. Your helper that builds the type names must turn it into `None`. |
| `true` ages are accepted | `bool` is a subclass of `int`. Test `isinstance(value, bool)` first. |
| `FileNotFoundError` for `out/report.json` | Create the parent folder before opening the file for writing. |
| The report lists `INC-3004` with 104 hours | Your `deduplicate` keeps the **last** copy of a ticket. It must keep the first, as in Session 02. |
| The config test fails on the paths | Join them to `path.parent`, the config file's folder, not to `Path.cwd()`. |
| `main` returns `None` | Every path through `main` must `return` an exit code. |

Remember the workflow: **Observe** (which check, which value?), **Hypothesize**, **Inspect** (in `python -i`), **Fix**, **Verify** (the whole checker, not just one check).

## Extension challenges (optional)

1. **Atomic writes.** If the job is killed halfway through `write_report`, the old report is gone and the new one is half-written. Write to `report.json.tmp` first, then `Path.replace()` it over the real file. Why is that safer, and what does `replace` guarantee?
2. **A Markdown report.** Add `write_markdown(report, path)` that renders the same data as a Markdown table, and an `"output_format"` option in `config.json` that chooses between the two. Use a dict of functions to dispatch (Part 1 of the concepts notebook).
3. **Command-line options.** Replace the hand-written `sys.argv` handling with the standard library's `argparse`, adding `--config` and `--output` options and an automatic `--help`.
4. **Fail-fast mode.** Add a `"strict": true` config option that makes the job stop with exit code `2` on the first rejected file. Where does that decision belong: in `load_exports`, or in `main`? Justify your choice in `NOTES.md`.

## Reflection

Answer briefly in `NOTES.md`:

1. Where in your code is each kind of failure **handled**, and why there? Draw the path an `ExportError` takes from `json.load` to the report.
2. `validate_ticket` returns a list of problems, while `read_export` raises an exception. Why do the two use different mechanisms?
3. Your type hints say `age_hours` is an `int`, yet you still had to check it by hand. When would Python check it for you, and what does Session 06's Pydantic change?
4. Compare your error handling with how you'd write this in Java or C#. What did you miss, and what was easier?

## Deliverables

Submit **one** of the following, as your course instructions specify:

- a link to a Git repository containing your project (push only to a repository you own; keep it private if you prefer), **or**
- a `.zip` of the project folder **without** `.venv/` and `out/`.

The submission must include:

- [ ] `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore` (including `out/`)
- [ ] `incident_report.py` with all functions implemented
- [ ] `ticket_summary.py` and `sample_tickets.py` from Session 02
- [ ] `check_report.py`, `config.json` and `data/`, unchanged
- [ ] `NOTES.md` with your Milestone 1, 2 and 8 answers and the reflection
- [ ] All acceptance criteria passing
