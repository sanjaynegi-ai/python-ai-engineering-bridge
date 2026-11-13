# Session 04: Modules, Packages, Classes and Testing

**Phase 1: Python for Experienced Developers** · Weekend 2 · 2-hour live session · **Milestone 1: Project 01**

## 1. Session overview

Your incident report works, but it's a pair of scripts held together by string keys and checked by hand-written checker scripts. This session gives it the structure of professional Python software: a `src/`-layout **package** with one responsibility per module, **dataclasses** for tickets, rejections and configuration, a **pytest** test suite, and project-wide **Ruff** configuration. You'll also learn to debug with breakpoints instead of print statements.

The workbook completes **Project 01**, the course's first checkpoint: a tested, installable Python tool that you could hand to a colleague.

## 2. Why this matters

Every Python codebase you'll meet in AI engineering, from FastAPI services and LLM integrations to RAG pipelines, is organised as packages and modules, models its data with classes, and is guarded by pytest. Reading those codebases means understanding how imports resolve, why a module runs only once, and where a fixture comes from. Contributing to them means writing tests that fail for the right reasons.

The most common problems at this stage are structural: a shadowed module, a circular import, a package that works in the terminal but not in the IDE, tests that pass alone and fail together. This session reproduces each one so that you'll recognise it when it happens for real.

## 3. Prerequisites

**Knowledge:** Sessions 01–03 completed. Your Session 03 `incident_report.py` and Session 02 `ticket_summary.py` pass their checkers, because you'll move that code into the package.

**Before the session:**

1. In the course repository, run `uv sync`. This session's notebooks run pytest and Ruff, which come with the course environment's `dev` dependency group.
2. In VS Code, make sure you can select a project's `.venv` as the interpreter (Session 01, Part 6). You'll use the debugger.

## 4. Learning objectives

By the end of this session you will be able to:

1. **Explain** how `import` resolves a name through `sys.modules` and `sys.path`, and **diagnose** shadowed, missing and circular imports.
2. **Refactor** a script into a `src/`-layout package with one responsibility per module and one-way dependencies, runnable as a command and with `python -m`.
3. **Write** Python classes with `__init__`, properties and dunder methods, and **compare** them with Java and C# classes.
4. **Model** domain objects with frozen dataclasses, `default_factory` and `@classmethod` constructors, and **choose** composition over inheritance.
5. **Test** behaviour with pytest using `assert`, fixtures, `conftest.py`, `tmp_path`, `parametrize` and `pytest.raises`, and **prove** that tests can fail.
6. **Configure** Ruff in `pyproject.toml`, and **interpret** its findings.
7. **Debug** with `breakpoint()`, `pytest --pdb` and the VS Code debugger.

## 5. Estimated time

| Activity | Time |
|---|---:|
| Live session | 2 hours |
| Concepts notebook (revision on your own) | 60 minutes |
| Debugging lab | 45 minutes |
| Practice quiz | 35 minutes |
| Workbook assignment (Project 01) | 2.5–3 hours |

## 6. Concepts covered

| Concept | Depth |
|---|---|
| Modules, `import` forms, `__name__`, `sys.modules`, `sys.path` | Independent implementation |
| Shadowing and circular imports | Independent implementation |
| Packages, `__init__.py`, `__main__.py`, the `src/` layout, absolute versus relative imports | Independent implementation |
| `[project.scripts]` and editable installs with `uv sync` | Independent implementation |
| Classes: `__init__`, `self`, attributes, `@property`, dunder methods, the `_private` convention | Independent implementation |
| `@dataclass`, `frozen=True`, `field(default_factory=...)`, `replace`, `asdict`, `@classmethod` | Independent implementation |
| Composition versus inheritance | Independent implementation |
| `typing.Protocol`, `TYPE_CHECKING` imports | Awareness |
| pytest: discovery, `assert`, fixtures, `conftest.py`, `tmp_path`, `capsys`, `parametrize`, `pytest.raises`, `--import-mode=importlib` | Independent implementation |
| Ruff configuration and rule families | Independent implementation |
| `breakpoint()`, pdb commands, `pytest --pdb`, the VS Code debugger | Independent implementation |
| Coverage and type checkers | Awareness (extension) |

### Live session plan

| Segment | Time | What happens |
|---|---:|---|
| Problem and intuition | 20 min | A new colleague, a `KeyError: 'teams'`, and a codebase nobody can test; the Java/C# equivalents of what we need |
| Visual explanation and demo | 20 min | How imports resolve; the `src/` layout; dataclasses replacing dicts; how pytest runs a test |
| Guided coding | 40 min | Start Project 01 together: copy the starter, run the failing acceptance tests, write `models.py` until `test_models.py` passes |
| Debugging challenge | 25 min | The debugging lab: shadowing, a script run inside a package, a circular import, and tests that can't fail |
| Recap and assignment briefing | 15 min | Key takeaways; the remaining workbook milestones; what "Project 01 complete" means |

## 7. Live demonstration

The instructor will:

1. Import a module three times and show its top-level code running once, then show `__name__` in a script versus a module.
2. Run a `src/`-layout package without and with the editable install, and explain why the failure is a feature.
3. Replace a ticket dict with a frozen dataclass, and show an editor catching `ticket.teams` before anything runs.
4. Trigger the dataclass mutable-default `ValueError` and fix it with `default_factory`.
5. Run a parametrized pytest suite with a failing boundary case, and read the assertion-rewriting output.
6. Set a breakpoint in a test with VS Code's **Debug Test**, and inspect a dataclass in the Variables panel.

## 8. Guided exercises

1. [`notebooks/01-concepts.ipynb`](notebooks/01-concepts.ipynb):
   - **Import once:** predict how often a module's code runs.
   - **The `src/` layout:** see a package fail and then succeed to import.
   - **Dataclasses:** frozen instances, `replace`, the mutable-default error, a `from_record` classmethod.
   - **pytest:** run a parametrized suite and read a failure; fix it.
   - **Ruff:** predict five findings in a small file.
2. [`notebooks/03-debugging-lab.ipynb`](notebooks/03-debugging-lab.ipynb): five broken projects to diagnose and fix (shadowing, script versus module, circular import, a test that can't fail, tests that share state).
3. [`notebooks/02-practice-quiz.ipynb`](notebooks/02-practice-quiz.ipynb): 10 self-check questions.

## 9. Independent assignment

[**Workbook: Project 01, the `incident-report` package**](workbook/assignment.md) (*Independent*: no AI coding assistant)

Restructure your Session 02 and 03 code into an installable package with typed dataclasses, make 48 provided acceptance tests pass, write at least 12 unit tests of your own (and prove they can fail), and debug the code with breakpoints. The starter project is in [`projects/01-python-data-processor`](../../projects/01-python-data-processor/README.md).

## 10. Expected deliverables

- The `incident-report` project, with `src/incident_report/` complete and tagged `project-01` in Git.
- `uv run pytest` passing: the 48 acceptance tests, unchanged, plus at least 12 of your own.
- `uv run ruff check .` and `uv run ruff format --check .` passing with the project's configuration.
- `NOTES.md` with milestone answers, two failing-test proofs and your reflection.

## 11. Common mistakes

| Mistake | Instead |
|---|---|
| A file named after a standard-library module (`json.py`, `logging.py`) | A distinctive name; check `module.__file__` when imports misbehave |
| Modules that import each other | One-way dependencies; shared code moves down to a lower module |
| Running `python src/pkg/module.py` | `uv run python -m pkg` or the installed command |
| Deep class hierarchies | Dataclasses plus composition; inheritance for exceptions |
| `tags: list[str] = []` in a dataclass | `field(default_factory=list)`, or a tuple in a frozen dataclass |
| `ticket.is_open()` on a property | `ticket.is_open` |
| `assert (x == y, "message")` | `assert x == y, "message"` |
| Module-level test data that tests modify | A fixture that returns fresh data per test |
| A test you've never seen fail | Break the code once and watch it fail |
| `breakpoint()` left in committed code | Remove it before committing |

## 12. Reading resources

Curated official documentation for this session: [`resources/references.md`](resources/references.md).

## 13. Reflection questions

1. Python has no `private` keyword. What keeps a large Python codebase maintainable without it?
2. When would you still pass a dict rather than a dataclass in Python code?
3. What would you look for when reviewing a colleague's pytest tests?
4. How is the `src/` layout's protection similar to Maven's or .NET's separation of `src/main` and `src/test`, and how is it different?

## 14. Interview questions

Practise answering these out loud, in two minutes or less each:

1. What happens, step by step, when Python executes `import mypackage.utils`?
2. What is a circular import, how does it fail, and how do you fix one?
3. What does `if __name__ == "__main__":` do, and what's the alternative in a package?
4. What does `@dataclass` generate? What changes with `frozen=True`?
5. Composition or inheritance: give an example of each that you'd defend in a code review.
6. What is a pytest fixture, and how does it differ from `setUp` in JUnit or xUnit?
7. How do you debug a failing test in Python?

## 15. Next-session preparation

**Session 05: HTTP and API Integration** starts Phase 2. You'll call REST APIs with HTTPX, handle timeouts and error status codes, keep credentials in environment variables, and test an API client without touching the network.

Before the session:

- Finish Project 01 and tag it. Project 02 builds on the same domain, and a checkpoint version is provided so that nobody is blocked.
- Make sure `uv sync` works in the course repository; Session 05 adds HTTPX to it.
