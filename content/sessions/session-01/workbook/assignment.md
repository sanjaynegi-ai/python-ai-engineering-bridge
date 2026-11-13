# Session 01 Assignment: A Reproducible `ops-toolkit` Project

**Type:** Independent. Complete this without an AI coding assistant; Session 13 covers AI-assisted work.
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb), Parts 1–7

---

## Business scenario

At Orbital Logistics (fictional), new platform engineers lose most of their first day to Python setup. The team lead has asked for two things:

1. A standard project setup that anyone can clone and run with one command, getting exactly the same dependency versions.
2. An **environment check** command, `ops-toolkit`, that a new engineer (or a CI job) runs first. It prints what it found and exits with a **non-zero exit code** if the environment is wrong, so that scripts and pipelines can rely on it.

You'll build both. The code is small; what you're really practising is the professional workflow around it.

## Learning objectives

By completing this assignment you will:

- **Create** a Python project with `uv`, pinned to Python 3.13.
- **Add** runtime and development dependencies, and **explain** the resulting changes to `pyproject.toml` and `uv.lock`.
- **Implement** a script that inspects its own runtime: interpreter, virtual environment and installed packages.
- **Reproduce** an environment from the lockfile alone.
- **Debug** a wrong-interpreter failure deliberately, and turn it into a clear, actionable error message.

## Prerequisites

- `uv` installed (`uv --version` prints 0.13 or newer). See the [session README](../README.md#prerequisites) if not.
- Git installed (`git --version`).
- VS Code with the Python extension, or another editor you're comfortable with.
- Concepts notebook Parts 1–7 completed.

Everything else (Python 3.13, the packages) uv will install for you.

---

## Project setup

Choose a folder **outside** the course repository for your own work, for example `~/skillup` or `C:\skillup`. Then run:

```bash
uv python install 3.13
uv init --no-package --python 3.13 ops-toolkit
cd ops-toolkit
```

You should see:

```text
Initialized project `ops-toolkit` at `.../ops-toolkit`
```

> **Why these flags?** `--no-package` gives you a simple single-file project; uv 0.13's default creates a packaged `src/` layout, which you'll build in Session 04. `--python 3.13` makes the result identical whichever Python happens to be your machine's default. (Each is explained in Part 4 of the concepts notebook.)

---

## Requirements

Your finished project must satisfy all of these:

| # | Requirement |
|---|---|
| R1 | The project is managed by uv, requires Python ≥ 3.13, and has `.python-version` set to `3.13`. |
| R2 | `rich` is a **runtime** dependency, and `ruff` is a **development** dependency. |
| R3 | `uv run main.py` prints a table containing: the Python version, the interpreter path, whether a virtual environment is active, and **each runtime dependency declared in `pyproject.toml`** with its installed version. |
| R4 | The list of dependencies is **read from `pyproject.toml`** at run time, not hard-coded. Adding a dependency later must appear in the report without any code changes. |
| R5 | The script exits with code **0** when every check passes, and code **1** when any check fails (Python version too old, not in a virtual environment, or a declared dependency missing). |
| R6 | When run with an interpreter that cannot import `rich`, the script prints a plain-text message naming the problem, the interpreter it is running on, and the fix (`uv run main.py`), then exits with code 1. **No traceback.** |
| R7 | `uv run ruff check .` and `uv run ruff format --check .` both pass. |
| R8 | Deleting `.venv` and running `uv sync --locked` restores a working environment, and `uv lock --check` passes. |

## Suggested structure

At the end your project should look like this. (`.venv/` exists locally but is git-ignored.)

```text
ops-toolkit/
├── .git/
├── .gitignore
├── .python-version
├── NOTES.md          ← you create this (milestones 2, 5 and the reflection)
├── README.md
├── main.py
├── pyproject.toml
└── uv.lock
```

> **Don't see `.gitignore` or `.git/`?** uv only creates them when Git is installed and the folder isn't already inside another Git repository. Install Git, or create the repository yourself with `git init`, and copy the `.gitignore` entries from Part 7 of the concepts notebook.

---

## Implementation milestones

### Milestone 1: Inspect what `uv init` created

1. List the files, including hidden ones (`ls -a` on macOS/Linux, `Get-ChildItem -Force` in PowerShell).
2. Open `pyproject.toml`, `.python-version` and `main.py`. Note that there is **no `.venv` and no `uv.lock` yet**.
3. Run the starter program:

   ```bash
   uv run main.py
   ```

   Expected output: uv reports creating a virtual environment, then `Hello from ops-toolkit!`.
4. List the files again. **Predict before you look:** which two new items appeared, and which command step created each one?

### Milestone 2: Add dependencies and read the diff

```bash
uv add rich
uv add --dev ruff
uv tree
```

1. Open `pyproject.toml`. Find where `rich` and `ruff` were recorded. Why are they in **different** sections?
2. Open `uv.lock` (read it; never edit it). `rich` is there, but so are packages you never asked for. Use the `uv tree` output to explain where each one comes from.
3. Commit your work so far: `git add .` and `git commit -m "Add rich and ruff"`. Run `git status` first, and confirm `.venv/` is **not** listed.

Create `NOTES.md` and write two or three sentences answering: *what is the difference between the `rich` entry in `pyproject.toml` and the `rich` entry in `uv.lock`?*

### Milestone 3: Implement the environment check

Replace the contents of `main.py`. Here is a suggested shape. The function names and signatures are a guide, and the bodies are yours to write:

```python
import sys
import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from rich.console import Console
from rich.table import Table

MINIMUM_PYTHON = (3, 13)
PYPROJECT_PATH = Path(__file__).parent / "pyproject.toml"


def python_version_ok(minimum: tuple[int, int]) -> bool: ...


def in_virtual_environment() -> bool: ...


def declared_dependencies(pyproject_path: Path) -> list[str]:
    """Return distribution names, e.g. ["rich"], from [project].dependencies."""
    ...


def installed_version(distribution_name: str) -> str | None:
    """Return the installed version, or None if it isn't installed."""
    ...


def main() -> int:
    """Build and print the report. Return 0 if all checks pass, otherwise 1."""
    ...


if __name__ == "__main__":
    raise SystemExit(main())
```

Hints, in the order you'll probably need them:

- **Version check:** `sys.version_info` compares directly with a tuple (concepts notebook, Part 2).
- **Virtual environment check:** compare `sys.prefix` and `sys.base_prefix` (Part 3).
- **Reading `pyproject.toml`:** `tomllib.load()` needs the file opened in **binary** mode (`"rb"`). The dependency strings look like `"rich>=15.0.0"`. You need just the name part, before any of the characters `<`, `>`, `=`, `!`, `~`, `[`, `;` or a space. Plain string methods are enough here; no regular expressions needed.
- **Installed version:** `importlib.metadata.version(name)` returns a version string, or raises `PackageNotFoundError`. Catch that exception and return `None`.
- **Why `Path(__file__).parent`?** So the script finds *its own* `pyproject.toml` whichever folder you run it from. Try running it from the parent folder later (`uv run --project ops-toolkit ops-toolkit/main.py`) to see why this matters.
- **Output:** a `rich.table.Table` with three columns (`Check`, `Value`, `Status`), printed with `Console().print(table)`. Pass `overflow="fold"` to the `Value` column so long interpreter paths wrap instead of being cut off.
- **Exit codes:** `raise SystemExit(main())` turns `main()`'s return value into the process exit code.

Check your progress:

```bash
uv run main.py
```

The report should look roughly like this. Your paths will differ, and the table borders depend on your terminal:

```text
                    ops-toolkit environment check
┌─────────────────────┬──────────────────────────────────────┬────────┐
│ Check               │ Value                                │ Status │
├─────────────────────┼──────────────────────────────────────┼────────┤
│ Python version      │ 3.13.x                               │ OK     │
│ Interpreter         │ /home/you/skillup/ops-toolkit/.venv/ │        │
│                     │ bin/python                           │        │
│ Virtual environment │ yes                                  │ OK     │
│ Dependency: rich    │ 15.0.0                               │ OK     │
└─────────────────────┴──────────────────────────────────────┴────────┘
Environment ready
```

Then check the exit code (expected: `0`):

```bash
# macOS / Linux / Git Bash
echo $?

# PowerShell
$LASTEXITCODE
```

**Experiment (R4):** run `uv add httpx`, then `uv run main.py`, without changing any code. A `Dependency: httpx` row should appear. Then `uv remove httpx`.

### Milestone 4: Break it on purpose

This is the debugging pattern from Part 6 of the concepts notebook. Practise it on a failure you caused yourself, so you can recognise it later in a real one.

1. **Observe.** Run your script with the *base* Python 3.13 interpreter, the one your `.venv` was created from, instead of the project's environment. `uv python find --system 3.13` prints that interpreter's path, and the command below runs it:

   ```bash
   # macOS / Linux / Git Bash
   "$(uv python find --system 3.13)" main.py

   # PowerShell
   & (uv python find --system 3.13) main.py
   ```

   This is exactly what happens when you type `python main.py` and the `python` on your `PATH` is a global interpreter. Using the explicit path makes the result the same on every machine. (Note that `--system` matters here: inside a project folder, plain `uv python find` returns the project's `.venv` interpreter.)

2. **Read the traceback bottom up** and copy it into `NOTES.md`. Answer: which line of *your* file failed? Why did your carefully written checks in `main()` never get a chance to run?

3. **Hypothesize and inspect.** Print `uv python find --system 3.13` on its own and compare it with the `Interpreter` row from Milestone 3. Write one sentence in `NOTES.md` explaining the failure.

4. **Verify** that `uv run main.py` still works and exits with `0`.

### Milestone 5: Make the failure helpful (R6)

The traceback from Milestone 4 is accurate but unhelpful to a new engineer. Change your script so that, when `rich` can't be imported, it prints something like:

```text
FAIL: cannot import 'rich' using the interpreter at /usr/bin/python3
This usually means the project's virtual environment is not being used.
Run the tool with: uv run main.py
```

and exits with code `1`.

Hints:

- The failure happens at the `from rich… import …` lines, so that's where the handling must go: wrap those imports in `try` / `except ModuleNotFoundError as error:`.
- `error.name` holds the name of the module that couldn't be found.
- Plain `print()` is the right tool here, because `rich` is exactly what's missing.
- `raise SystemExit(1) from None` exits with code 1 without printing a chained traceback.

Re-run the Milestone 4 command. You should now see your message, and the exit code should be `1`.

### Milestone 6: Prove it's reproducible (R8)

1. Delete the environment:

   ```bash
   # macOS / Linux / Git Bash
   rm -rf .venv

   # PowerShell
   Remove-Item -Recurse -Force .venv
   ```

2. Rebuild it strictly from the lockfile, then run:

   ```bash
   uv sync --locked
   uv run main.py
   ```

3. Confirm that the lock matches `pyproject.toml`:

   ```bash
   uv lock --check
   ```

4. Simulate a teammate. Clone your repository into a second folder and run it there:

   ```bash
   cd ..
   git clone ops-toolkit ops-toolkit-teammate
   cd ops-toolkit-teammate
   uv run main.py
   ```

   Compare the dependency versions with your original. They must be identical. Why, given that only `pyproject.toml` and `uv.lock` were copied? Answer in `NOTES.md`. (Commit your latest changes before cloning, otherwise the clone won't include them.)

### Milestone 7: Quality gate (R7)

```bash
uv run ruff format .
uv run ruff check .
uv run ruff format --check .
```

Fix anything `ruff check` reports, then commit.

---

## Acceptance criteria

Your submission is complete when **every** command below behaves as described. Run them from the project folder.

| Command | Expected result |
|---|---|
| `uv run main.py` | Prints the report with all checks `OK`, and exit code `0` |
| The Milestone 4 command (base interpreter, not `uv run`) | Prints your plain-text `FAIL:` message, **no traceback**, exit code `1` |
| `uv lock --check` | Succeeds (exit code `0`) |
| `uv run ruff check .` | `All checks passed!` |
| `uv run ruff format --check .` | Reports every file as already formatted |
| `git status` | Clean working tree; `.venv/` is not tracked |
| `git ls-files` | Includes `pyproject.toml`, `uv.lock`, `.python-version`, `main.py`, `NOTES.md` |
| `grep -n rich pyproject.toml` (or `Select-String rich pyproject.toml`) | `rich` appears under `dependencies`, not under `[dependency-groups]` |

## Testing

There are no automated tests in this assignment. pytest arrives in Session 04, and we'll add tests to this kind of code then. For now, the **acceptance criteria table is your test suite**: run every row, and check both the output and the exit code.

One extra manual test of R5: temporarily change `MINIMUM_PYTHON` to `(3, 99)`, run `uv run main.py`, and confirm the version row shows `FAIL` and the exit code is `1`. Then change it back.

## Debugging guidance

| You see | Where to look |
|---|---|
| uv says it can't find or download Python 3.13 | Run `uv python install 3.13` and read its error. On corporate networks, a proxy often blocks the download. Check `uv python list --only-installed` afterwards. |
| Git prints `LF will be replaced by CRLF` (Windows) | Harmless: Git is normalising line endings. No action needed. |
| `ModuleNotFoundError: No module named 'rich'` from `uv run main.py` | Did `uv add rich` run in **this** folder? Check `pyproject.toml`. Then run `uv sync`. |
| `TypeError: File must be opened in binary mode` | `tomllib.load()` needs `open(path, "rb")`. |
| `KeyError: 'project'` | You're reading the wrong `pyproject.toml`. Print `PYPROJECT_PATH` and check it. |
| The dependency row shows `missing` for something like `rich>` | Your name parsing doesn't strip every version operator. Print the raw strings from `pyproject.toml` and test your parsing on them. |
| `UnicodeEncodeError: 'charmap' codec can't encode character` (Windows) | Your console can't display a character you printed (for example ✓ or ✗). Use Windows Terminal, set the environment variable `PYTHONUTF8=1`, or stick to plain ASCII such as `OK`/`FAIL`. |
| The exit code is always `0` | Is `main()` *returning* a number, and are you calling `raise SystemExit(main())`, not just `main()`? |
| VS Code underlines `rich` in red, but `uv run` works | VS Code is using a different interpreter. Run **Python: Select Interpreter** and choose `./.venv`. |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | You don't need activation: use `uv run`. |

When you're stuck: **Observe** (what exactly happened?), **Hypothesize** (what could cause it?), **Inspect** (print the value, check the interpreter), **Fix**, **Verify** (re-run the *original* command).

## Extension challenges (optional)

1. **Machine-readable output.** Add a `--json` flag (check `sys.argv`) that prints the results as JSON with `json.dumps`, instead of the table, so CI could parse them. Keep the same exit codes.
2. **Check the toolchain too.** Use `shutil.which("uv")` and `shutil.which("git")` to report whether those tools are on `PATH`. Should a missing `git` be a `FAIL` or a warning? Justify your choice in `NOTES.md`.
3. **Lock awareness.** Run `uv lock --check` from inside the script with `subprocess.run(...)` and report whether the lockfile is up to date. What happens to your tool's exit code if `uv` itself isn't installed?
4. **Read ahead.** Run `uv init --python 3.13 ops-toolkit-packaged` (without `--no-package`) in a scratch folder and compare the layout. What is `[project.scripts]` for? You'll use this layout in Session 04.

## Reflection

Answer these in `NOTES.md`, briefly; a few sentences each is plenty:

1. Your team's CI uses `uv sync --locked`. A colleague proposes switching to plain `uv sync` "because `--locked` keeps failing." What would you say?
2. In Milestone 4, your checks in `main()` never ran. What does that tell you about **when** module-level imports execute, and how does that change where you put error handling?
3. Map `pyproject.toml`, `uv.lock` and `.venv/` to their equivalents in the ecosystem you know best. Where does the analogy break down?
4. Which part of this assignment surprised you most, coming from your main language?

## Deliverables

Submit **one** of the following, as your course instructions specify:

- a link to a Git repository containing your project (push only to a repository you own; keep it private if you prefer), **or**
- a `.zip` of the project folder **without** `.venv/`.

The submission must include:

- [ ] `pyproject.toml`, `uv.lock`, `.python-version`, `main.py`, `README.md`, `.gitignore`
- [ ] `NOTES.md` with the Milestone 2 answer, the Milestone 4 traceback and explanation, the Milestone 6 answer, and the reflection answers
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
