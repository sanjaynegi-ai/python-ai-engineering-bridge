# Project Structure

Where things go in a Python project, why, and the mistakes that cause most import errors. Every project in the course follows this shape; Session 04 explains it.

## The layout

```text
incident-report/
├── pyproject.toml          name, Python version, dependencies, entry points, tool settings
├── uv.lock                 exact versions (commit it)
├── .python-version         3.13
├── .gitignore              .venv/, __pycache__/, .env, caches, generated output
├── README.md               what it does, how to set up, run and test it
├── src/
│   └── incident_report/    the package: its name is what you import
│       ├── __init__.py     makes the folder a package (often just a docstring)
│       ├── __main__.py     optional: lets `python -m incident_report` run it
│       ├── models.py       data: dataclasses (later, Pydantic models)
│       ├── loading.py      reading files
│       ├── report.py       the logic
│       └── cli.py          main(): argument parsing and exit codes, nothing else
└── tests/
    ├── conftest.py         shared fixtures
    ├── acceptance/         tests that define "done"
    └── unit/               your own tests
```

**Names:** the distribution (in `pyproject.toml`, on PyPI, and the command) uses hyphens: `incident-report`. The package (the folder, and what you import) uses underscores: `incident_report`.

## Why `src/`?

Without it, Python can import your package straight from the project folder, so tests pass even when the installed package is broken or missing files. With `src/`, the only way to import `incident_report` is through the environment `uv sync` built, which is how users will get it too. `uv init` creates this layout.

## The parts of `pyproject.toml`

```toml
[project]
name = "incident-report"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["pydantic>=2.14"]          # uv add maintains this list

[project.scripts]
incident-report = "incident_report.cli:main"   # command = "package.module:function"

[build-system]
requires = ["uv_build>=0.13.1,<0.14.0"]
build-backend = "uv_build"

[dependency-groups]
dev = ["pytest>=9.1.1", "ruff>=0.17.1"]    # uv add --dev maintains this one

[tool.ruff]
line-length = 100

[tool.pytest]
testpaths = ["tests"]
addopts = ["-ra", "--import-mode=importlib"]
```

`--import-mode=importlib` lets two test files share a name in different folders (`tests/unit/test_models.py` and `tests/acceptance/test_models.py`).

## Imports

- Use **absolute** imports from the package root: `from incident_report.models import Ticket`.
- Import modules in this order, separated by blank lines: the standard library, third-party packages, your own package. `ruff check` (rule `I`) sorts them; `ruff check --fix` does it for you.
- A module runs top to bottom the first time it's imported. Keep side effects (reading files, network calls, starting things) out of module level: put them in functions, called from `main()`.
- **Circular imports** (`a` imports `b`, which imports `a`) usually mean a missing module: move what both need into a third one, such as `models.py`.

## Common errors

| Error | Usual cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'incident_report'` | Running `python` instead of `uv run python`, or the editor uses another interpreter | `uv run ...`; select `.venv` in your editor |
| The same, for a third-party package | It isn't in `pyproject.toml`, or `uv sync` wasn't run | `uv add <package>` |
| `ImportError: cannot import name 'X' from partially initialized module` | A circular import | Move the shared code to its own module |
| `ImportError: attempted relative import with no known parent package` | Running a module that uses relative imports (`from .models import Ticket`) as a script, `python src/incident_report/cli.py` | Run the command, or `uv run python -m incident_report.cli` |
| Tests import an old version of your code | A stray copy of the package outside `src/`, or another installed copy | Keep one copy, in `src/`; `uv sync` |
| `import file mismatch` from pytest | Two test files with the same name, without `--import-mode=importlib` | Add it to `[tool.pytest]` |
<!-- release:3 -->

## Settings and secrets (Sessions 05 and 06)

```text
├── .env.example            every setting, with placeholders and comments: commit it
├── .env                    your real values: never commit it (it's in .gitignore)
└── src/incident_api/
    └── settings.py         a pydantic-settings class that reads the environment and .env
```

Read settings in one place, at startup, and pass them to what needs them. Code deep inside the application shouldn't read `os.environ` itself: it makes tests depend on your shell.
<!-- /release:3 -->
<!-- release:4 -->

## A service (Sessions 07 and 08)

```text
src/incident_api/
├── api.py          routes and the application factory: HTTP in, HTTP out
├── schemas.py      request and response models (the API's contract)
├── service.py      the business logic, independent of HTTP
├── models.py       domain data
├── settings.py     configuration
└── errors.py       the service's own exceptions, mapped to status codes in api.py
```

The rule: routes translate HTTP to calls on the service and back; the service never imports FastAPI. Then the same logic serves a CLI, a test or a queue consumer.
<!-- /release:4 -->
<!-- release:5 -->

## An application that calls an LLM (Sessions 09 to 12)

Keep everything provider-specific in one module behind a small protocol (`llm.py` with a `Triager` in Project 03; `generation.py` with a `Generator` in the capstone), the instructions in `prompts.py`, and the model's output contract in a Pydantic model. Then tests replace the provider with a fake, and changing providers changes one file.
<!-- /release:5 -->

## Further reading

- [Python Packaging User Guide: `src` layout versus flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).
- [The import system](https://docs.python.org/3.13/reference/import.html), for the details behind the errors above.
- [`uv-cheatsheet.md`](uv-cheatsheet.md).
