# uv Cheatsheet

Recipes for the jobs you'll do again and again. Each command is explained in [`docs/setup-uv.md`](../docs/setup-uv.md), and Session 01 shows why it works. The course uses **uv 0.13 or newer**.

## Start a new project

```bash
uv init incident-tool            # a package with a src/ layout, a console script and a Git repository
cd incident-tool
uv python pin 3.13               # writes .python-version
uv add httpx pydantic            # runtime dependencies: pyproject.toml and uv.lock
uv add --dev pytest ruff         # development tools, in the dev group
uv run incident-tool             # prints "Hello from incident-tool!"
git add . && git commit -m "Initial project"
```

Commit `pyproject.toml`, `uv.lock` and `.python-version`. Never commit `.venv/`. `uv init` copies your name and email from Git's configuration into `authors` in `pyproject.toml`: remove them before you publish a project you don't want them in.

## Start from someone else's project

```bash
git clone <repository-url>
cd <project>
uv sync                          # creates .venv/ exactly as the lockfile says
uv run pytest
```

If `uv sync` says the lockfile needs updating and you didn't change anything, someone committed `pyproject.toml` without running `uv lock`. Run `uv lock`, check the diff, and commit it.

## Day to day

| I want to... | Run |
|---|---|
| Run my code | `uv run python main.py`, or the project's command: `uv run <name>` |
| Run the tests, or one test | `uv run pytest`, `uv run pytest tests/test_models.py::test_priority -x` |
| Lint and format | `uv run ruff check .`, `uv run ruff format .` |
| Add a library | `uv add <package>` |
| Add a library only for tests or tools | `uv add --dev <package>` |
| Remove a library | `uv remove <package>` |
| See why a package is installed | `uv tree` (or `uv tree --invert --package <name>`) |
| Upgrade one library | `uv lock --upgrade-package <package>`, then `uv sync` |
| Upgrade everything within the constraints | `uv lock --upgrade`, then `uv sync`, then run the tests |
| Check the lockfile in CI | `uv lock --check`, then `uv sync --locked` |
| Install without the network | add `--offline`: uv uses packages it downloaded before |
| Try a tool without adding it | `uvx ruff check .` (runs the tool in a temporary environment) |

## Python versions

| I want to... | Run |
|---|---|
| See what's installed and available | `uv python list` |
| Install a version | `uv python install 3.13` |
| Use a version for this project | `uv python pin 3.13` |
| Check which interpreter `uv run` uses | `uv run python -c "import sys; print(sys.executable)"` |

## Fix it

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError` for a package you added | You ran `python` instead of `uv run python`, or your editor uses another interpreter. Point VS Code at `.venv`: [`docs/setup-vscode.md`](../docs/setup-vscode.md) |
| `uv: command not found` right after installing | Open a new terminal, so it picks up the updated `PATH` |
| Downloads fail behind a corporate proxy | `uv sync --system-certs`; see [`docs/troubleshooting.md`](../docs/troubleshooting.md) |
| `.venv` seems broken | Delete `.venv/` and run `uv sync`: it's rebuilt from the lockfile |
| A command needs a package for a minute | `uv run --with <package> python ...` (nothing is added to the project) |
| `pip install` "worked" but `uv run` can't import it | pip installed into another environment. Use `uv add` |

## Further reading

- [uv: working on projects](https://docs.astral.sh/uv/guides/projects/) and the [command reference](https://docs.astral.sh/uv/reference/cli/).
<!-- release:2 -->
- [`project-structure.md`](project-structure.md): what goes where in a uv project.
<!-- /release:2 -->
