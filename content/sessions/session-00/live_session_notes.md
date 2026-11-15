# Python for Experienced Java Engineers

## Session 1 --- Learner Notes and Self-Paced Workbook

**Audience:** Java engineers moving into Python-based AI engineering\
**Format:** Windows PowerShell commands, runnable `.py` modules, Java
comparisons, explanations, exercises\
**Suggested guided duration:** 2 hours (self-paced learners may need
longer)\
**Target runtime:** Python 3.12\
**Project:** `ai-python-bridge`

> **Scope:** This guide covers Python runtime selection, `uv`, virtual
> environments, dependencies, project files, Python syntax and types,
> collections, functions, exceptions, packages/imports, file I/O, a tiny
> *keyword* retriever, and basic `pytest`. It does **not** teach
> Pydantic, FastAPI, `asyncio`, Streamlit, Gradio, LangChain, an
> embedding-backed retriever, or a production RAG system. Those are
> future sessions.
>
> **Prior knowledge:** You know Java, IDEs, build tools, classes,
> packages, exception handling, collections, and testing. You also
> already know at a conceptual level what RAG, tokens, chunking,
> embedding vectors, and cosine similarity mean.
>
> **Execution rule:** Run PowerShell commands from the project root
> unless a section says otherwise. Source files are shown with their
> exact paths. Don't paste shell commands into Python files.

------------------------------------------------------------------------

## Learning outcomes and roadmap

After working through this guide, you should be able to:

1.  Explain why `python` and `uv run python` can invoke different
    interpreters.
2.  Install and select Python 3.12 with `uv` without replacing existing
    Python installations.
3.  Create a package-oriented Python project, identify
    `.python-version`, `.venv`, `pyproject.toml`, and `uv.lock`, and
    manage dependencies.
4.  Read and write Python functions, control flow, type hints,
    collections, comprehensions, lambdas, and exceptions.
5.  Explain a Python module vs a package and use `__init__.py`, absolute
    imports, and `python -m`.
6.  Run a file-backed keyword retriever and test it with `pytest`.
7.  Change the implementation independently, reason about a failure, and
    verify behavior.

### Suggested pacing

  Minutes    Topic
  ---------- --------------------------------------------------------------
  00--10     Java-to-Python mental model
  10--30     Python runtime selection, `uv`, project and dependency files
  30--45     Functions, variables, type hints, control flow
  45--60     Collections, comprehensions, `None`, exceptions
  60--75     Modules, packages, `__init__.py`, imports
  75--90     Build a small keyword retriever
  90--105    Tests, guided questions, debugging
  105--120   Independent extension and workbook reflection

------------------------------------------------------------------------

# 1. Translate the Java mental model

  ---------------------------------------------------------------------------------------
  Familiar Java concept       Python concept                      Important difference
  --------------------------- ----------------------------------- -----------------------
  JDK / JVM selection         Python interpreter selection        Different environments
                                                                  can use different
                                                                  interpreters.

  Maven / Gradle              `uv` for                            `uv` also manages
                              Python/version/project/dependency   environments; packaging
                              workflows                           can involve separate
                                                                  build backends.

  `pom.xml` / `build.gradle`  `pyproject.toml`                    TOML, not YAML;
                                                                  metadata and tool
                                                                  configuration have
                                                                  Python-specific
                                                                  conventions.

  Resolved dependency graph   `uv.lock`                           uv-generated lockfile
                                                                  records exact
                                                                  resolution.

  Per-project                 `.venv`                             Local Python
  dependencies/classpath                                          interpreter plus
                                                                  installed packages.

  Maven Central               PyPI or another configured package  Different repository
                              index                               and artifact
                                                                  conventions.

  `package com.example;`      `ai_python_bridge/` and             Python importable
                              `__init__.py`                       modules can execute
                                                                  top-level code.

  `public static void main`   `def main()` plus                   No mandatory enclosing
                              `if __name__ == "__main__"`         class.

  `List`, `Map`, `Set`        `list`, `dict`, `set`               Built-in mutable
                                                                  collections.

  Java Streams                comprehensions, generators,         List comprehensions are
                              iterators                           eager; generators are
                                                                  lazy.

  `null`                      `None`                              Test with `is None`.

  JUnit                       `pytest`                            Test functions and
                                                                  `assert` are idiomatic.
  ---------------------------------------------------------------------------------------

**Mental model:** Python reduces ceremony, but not the need for
engineering discipline. Modules, dependency isolation, error handling,
testing, and readable contracts are still essential.

------------------------------------------------------------------------

# 2. First, investigate which Python you're running

These steps are important if Python is already installed on Windows and
`uv` seems to use a different version.

## 2.1 Compare two commands outside a project

Open **PowerShell** in an empty folder, for example:

``` powershell
PS C:\demo\demo-1>
```

Run:

``` powershell
python --version
uv run python --version
```

An *illustrative* result from the original investigation was:

``` text
Python 3.13.1
Python 3.13.16
```

**What each part means:**

-   `python`: asks Windows to find an executable named `python`
    (normally using command resolution and `PATH`).
-   `--version`: tells that executable to print its version.
-   `uv`: starts the `uv` command-line tool.
-   `run`: tells uv to execute a command.
-   The `python --version` following `uv run` is the command uv runs,
    not an option to `uv`.
-   In a folder without a project, uv may select a managed/discovered
    interpreter according to its selection rules.

**Why they can differ:** One command uses the system's normal Python
resolution; the other uses uv's own interpreter/project discovery.
Neither output alone identifies the executable path.

## 2.2 Find available Python commands

``` powershell
where.exe python
```

Illustrative output:

``` text
C:\installations\Python\python.exe
C:\Users\<your-user>\AppData\Local\Microsoft\WindowsApps\python.exe
```

**Explanation:**

-   `where.exe` is the Windows executable search tool. Use `.exe`
    explicitly because PowerShell also has an alias `where` for
    `Where-Object`.
-   The first path can be a manually installed Python.
-   `WindowsApps\python.exe` may be an *app execution alias*, not a
    distinct complete Python installation.
-   Your output may contain different paths or only one path.

For the exact Python currently executing:

``` powershell
python -c "import sys; print(sys.executable)"
uv run python -c "import sys; print(sys.executable)"
```

**Line-by-line of the Python expression:**

-   `-c`: Python command-line switch to execute the next argument as
    code.
-   `import sys`: imports the standard-library `sys` module.
-   `;`: separates statements written on one line (not usually needed in
    normal `.py` files).
-   `print(sys.executable)`: displays the interpreter executable's path.

A uv-managed interpreter outside a project may be under a uv-managed
Python installation directory. **Inside a uv project**, the printed path
will usually be `.venv\Scripts\python.exe`.

## 2.3 Running an exact Windows executable

PowerShell treats a quoted path as text unless you invoke it. Use the
call operator `&`:

``` powershell
& "C:\installations\Python\python.exe" --version
```

If you want to investigate a WindowsApps alias:

``` powershell
& "$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe" --version
```

-   `&`: execute the path that follows.
-   Quotes: preserve spaces in paths.
-   `$env:LOCALAPPDATA`: reads an environment variable in PowerShell.
-   `--version`: passed to that executable.

**Do not conclude that two paths represent two separate Python
installations solely because both print a version.**

### Checkpoint A

Can you answer:

1.  Which Python runs when you type `python`?
2.  Which Python runs when you type `uv run python`?
3.  Where did you find each executable?

If not, rerun `sys.executable` and inspect the paths before proceeding.

------------------------------------------------------------------------

# 3. Install Python 3.12 and create a uv project

## 3.1 Verify uv and install Python

``` powershell
uv --version
uv python install 3.12
uv python list --only-installed
```

**Explanation:**

-   `uv --version`: displays the installed `uv` version.
-   `uv python install 3.12`: downloads/installs a uv-managed Python
    from the requested **3.12 series**.
-   `uv python list --only-installed`: lists interpreter installations
    known to uv that are already installed. The `--only-installed` flag
    is a filter.

**Does this replace a preexisting Python 3.13 installation?** No. A
uv-managed 3.12 interpreter can coexist with manually installed Python
3.13 and other uv-managed versions. Your exact patch version may differ.

## 3.2 Initialize a package-oriented project

Execute **one command at a time** in the parent folder where you want to
create the project:

``` powershell
uv init --package --python 3.12 ai-python-bridge
cd ai-python-bridge
uv add --dev pytest
```

**Command-by-command:**

1.  `uv init`: create the project scaffold.
2.  `--package`: choose a package project, with an importable Python
    package under `src/` and build configuration.
3.  `--python 3.12`: select the project's Python version preference; uv
    usually records it in `.python-version`.
4.  `ai-python-bridge`: destination/project name.
5.  `cd ai-python-bridge`: enter the generated project directory.
6.  `uv add --dev pytest`: add `pytest` to the development dependency
    group, update project/lock metadata, and normally sync the
    environment.

Now run:

``` powershell
uv run python --version
uv run python -c "import sys; print(sys.executable)"
uv run pytest --version
```

Expected interpreter version: `Python 3.12.x`. Expected interpreter
executable: a path resembling:

``` text
C:\demo\demo-1\ai-python-bridge\.venv\Scripts\python.exe
```

> **Habit to build:** Use `uv run` when running Python or project tools.
> You normally do not need to activate `.venv` manually.

## 3.3 What files did uv create?

After initialization and installing pytest, the project should look
approximately like this:

``` text
ai-python-bridge/
├── .python-version
├── .gitignore
├── .venv/                       # created on sync/run; do not commit
├── pyproject.toml
├── uv.lock                      # created during dependency resolution
├── README.md
└── src/
    └── ai_python_bridge/
        └── __init__.py
```

The project is named `ai-python-bridge` (hyphenated distribution name);
the Python package is `ai_python_bridge` (underscores in a legal import
name).

### Project anatomy diagram

``` text
pyproject.toml ── dependency requirements ──┐
                                            ▼
                                           uv
                                            │
                      ┌─────────────────────┴──────────────────┐
                      ▼                                        ▼
                 uv.lock                                   .venv/
          resolved package versions             interpreter + installed packages
                                                               │
                                                               ▼
                                                uv run python -m ...
```

-   `pyproject.toml` expresses *what the project requires*.
-   `uv.lock` captures *what dependency versions were resolved*.
-   `.venv` contains *what is installed for this working environment*.
-   `uv run` executes through the project environment.

## 3.4 Understand the files

### `.python-version`

Typical content:

``` text
3.12
```

Records the interpreter version preference. It doesn't install Python by
itself. Also distinguish it from `requires-python` in project metadata:
that declaration is a *compatibility range*, not necessarily an exact
runtime selection.

### `.gitignore`

Typical entries:

``` gitignore
.venv/
__pycache__/
*.py[cod]
dist/
```

Generated environments, bytecode caches, and build outputs do not belong
in source control. Your scaffold may have more entries.

### `.venv/`

Typical Windows structure:

``` text
.venv/
├── Lib/
│   └── site-packages/
├── Scripts/
│   ├── python.exe
│   └── Activate.ps1
└── pyvenv.cfg
```

Think of `.venv` as the **isolated Python environment for one project**,
not a Docker container. Do not manually edit or commit it. It can be
recreated.

### `pyproject.toml`

Representative excerpt (keep the file generated by your installed uv;
exact constraints/backend may differ):

``` toml
[project]
name = "ai-python-bridge"
version = "0.1.0"
description = "Python bridge for Java engineers"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = [
    "pytest>=8",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Explanation by line:**

-   `[project]`: standard project metadata section.
-   `name`: distribution/project name.
-   `version`: project version.
-   `description`: project purpose.
-   `readme`: referenced README document.
-   `requires-python`: allowed interpreter versions, *not* a pin to
    exactly 3.12.
-   `dependencies`: required runtime packages.
-   `[dependency-groups]`: optional groups of dependencies.
-   `dev`: development tools such as pytest.
-   `[build-system]`: configuration for the Python packaging build
    backend. The generated backend can differ.

**Java connection:** This is a useful comparison with `pom.xml`, but it
is **TOML, not `pyproject.yaml`**, and Python's build backend is a
separate mechanism.

### `uv.lock`

Machine-generated lockfile with resolved package versions, dependencies,
sources, and other package metadata. The real file is substantially
longer than its conceptual description here.

-   Commit it for an application project.
-   Do **not** hand-edit it.
-   `pyproject.toml` is *declarative requirements*; `uv.lock` is
    *resolved versions and dependency graph*.

### `README.md`

Human-oriented project documentation. Edit it to explain how to set up,
run, and test your project.

### `src/` and `__init__.py`

`src/` contains application package source. `__init__.py` marks a
**regular** Python package; it can be empty, or contain package-level
exports or initialization. Namespace packages can also exist without it,
but we use a regular package here.

------------------------------------------------------------------------

# 4. Dependency management in uv

Run these in `ai-python-bridge/`:

``` powershell
uv add httpx
uv tree
uv remove httpx
uv sync
```

  -----------------------------------------------------------------------
  Command                 What happens            Java analogy
  ----------------------- ----------------------- -----------------------
  `uv add httpx`          Declares a runtime      Add a dependency and
                          dependency, resolves    resolve it
                          it, updates lockfile    
                          and environment by      
                          default                 

  `uv tree`               Shows direct and        Maven/Gradle dependency
                          transitive dependencies tree

  `uv remove httpx`       Removes declaration and Remove dependency and
                          synchronizes            re-resolve
                          dependencies by default 

  `uv sync`               Reconciles installed    Reproducible dependency
                          environment with        installation
                          project and lockfile    
  -----------------------------------------------------------------------

### What changes?

  ---------------------------------------------------------------------------
  Operation           `pyproject.toml`   `uv.lock`          `.venv`
  ------------------- ------------------ ------------------ -----------------
  `uv add httpx`      Adds requirement   Resolves/updates   Installs packages

  `uv tree`           No intended change No intended change No intended
                                                            change

  `uv remove httpx`   Removes            Resolves/updates   Removes unused
                      requirement                           packages

  `uv sync`           No intended change Uses/updates lock  Aligns
                                         as needed          environment
  ---------------------------------------------------------------------------

Transitive packages may stay installed when other dependencies still
require them.

## 4.1 Why pip may be missing

Try:

``` powershell
uv run python -m pip --version
```

Possible output:

``` text
...\python.exe: No module named pip
```

This **does not mean the environment is broken**. `uv` has its own
resolver and installer; `pip` is not required for ordinary uv workflows.
The syntax `python -m pip` asks the selected Python to locate and run a
Python module called `pip`. If you truly need it *inside the
environment*, you can add it explicitly:

``` powershell
uv add --dev pip
uv run python -m pip --version
```

For this course you do **not** need pip. If you did add it for
demonstration, it is optional to remove it with:

``` powershell
uv remove --dev pip
```

## 4.2 Environment troubleshooting checklist

``` powershell
python --version
uv run python --version
where.exe python
python -c "import sys; print(sys.executable)"
uv run python -c "import sys; print(sys.executable)"
uv tree
uv sync
```

Check, in order:

1.  **Working directory:** Are you inside `ai-python-bridge/`?
2.  **Interpreter:** Does `uv run` point to the expected `.venv`?
3.  **Version preference:** Does `.python-version` say `3.12`?
4.  **Dependency declaration:** Is the package in `pyproject.toml`?
5.  **Resolved state:** Does `uv tree` display the dependency?
6.  **Environment sync:** Does `uv sync` complete successfully?
7.  **Typos:** Are import names and package names spelled correctly?

------------------------------------------------------------------------

# 5. Your first Python module: syntax and functions

Create **`src/ai_python_bridge/syntax_demo.py`**:

``` python
def greet(name: str) -> str:
    message = f"Welcome to AI Engineering, {name}"
    return message


def main() -> None:
    engineer = "Java Developer"
    experience = 10
    print(greet(engineer))
    print(f"Experience: {experience} years")


if __name__ == "__main__":
    main()
```

Run from project root:

``` powershell
uv run python -m ai_python_bridge.syntax_demo
```

Expected output:

``` text
Welcome to AI Engineering, Java Developer
Experience: 10 years
```

## Explain the code line by line

1.  `def greet(...):` defines a function; unlike Java, no enclosing
    class is required.
2.  `name: str` is a type annotation for the parameter.
3.  `-> str` annotates the intended return type.
4.  `message = f"..."` binds a name to a formatted string. The `{name}`
    section is interpolated.
5.  `return message` returns the result.
6.  `def main() -> None:` defines a function expected to return no
    useful value.
7.  `engineer = ...` and `experience = ...` bind names to objects
    without mandatory local type declarations.
8.  `print(greet(engineer))` nests a function call.
9.  `print(f"Experience: ...")` formats the output.
10. `if __name__ == "__main__":` checks whether this module is being
    executed as the entry point.
11. `main()` starts execution.

### Similar Java

``` java
public class SyntaxDemo {
    static String greet(String name) {
        String message = "Welcome to AI Engineering, " + name;
        return message;
    }

    public static void main(String[] args) {
        String engineer = "Java Developer";
        int experience = 10;
        System.out.println(greet(engineer));
        System.out.println("Experience: " + experience + " years");
    }
}
```

### Important differences

-   Python uses **indentation** to form blocks, rather than braces. Use
    four spaces per level.
-   Python does not require semicolons.
-   Function and variable type annotations do **not** automatically
    enforce types at runtime.
-   Java-like design skills still apply; Python simply has different
    language conventions.

Try a small experiment:

``` python
age: int = 42
age = "forty-two"
print(age)
```

This prints `forty-two` at runtime; a static type checker can flag the
incompatible assignment. Type hints still help readability, tooling, and
future schema validation.

------------------------------------------------------------------------

# 6. Control flow, types, equality, and mutation

## 6.1 `if` / `elif` / `else` and loops

Create **`src/ai_python_bridge/control_flow.py`**:

``` python
def classify_latency(latency_ms: int) -> str:
    if latency_ms < 100:
        return "FAST"
    elif latency_ms < 500:
        return "ACCEPTABLE"
    else:
        return "SLOW"


latencies = [45, 220, 700]

for latency in latencies:
    print(latency, classify_latency(latency))
```

Run:

``` powershell
uv run python -m ai_python_bridge.control_flow
```

Output:

``` text
45 FAST
220 ACCEPTABLE
700 SLOW
```

**Line-by-line:**

1.  `def` starts a typed function definition.
2.  `if latency_ms < 100:` tests the first condition.
3.  `return "FAST"` exits with a result.
4.  `elif` is Python's `else if`.
5.  The second `return` handles the middle range.
6.  `else` covers the remaining values.
7.  `latencies = [...]` creates a list.
8.  `for latency in latencies:` iterates directly over each value.
9.  `print(...)` calls the classifier for each input.

Java equivalent:

``` java
static String classifyLatency(int latencyMs) {
    if (latencyMs < 100) return "FAST";
    else if (latencyMs < 500) return "ACCEPTABLE";
    return "SLOW";
}

for (int latency : new int[]{45, 220, 700}) {
    System.out.println(latency + " " + classifyLatency(latency));
}
```

## 6.2 Names, objects, `is` and `==`

Try this in **`src/ai_python_bridge/identity_demo.py`**:

``` python
value = 100
print(type(value))

value = "one hundred"
print(type(value))

items = [1, 2]
other = items

other.append(3)

print(items)
print(items is other)
print(items == other)
```

**Line-by-line:**

1.  `value = 100` binds a name to an `int` object.
2.  `type(value)` inspects the runtime type.
3.  Reassigning `value = "one hundred"` binds the name to a `str`
    object.
4.  The second `type` prints `str`.
5.  `items = [1, 2]` creates a mutable list.
6.  `other = items` creates an alias to the **same object**, not a copy.
7.  `append(3)` mutates that list, visible through both names.
8.  `print(items)` shows `[1, 2, 3]`.
9.  `is` compares *object identity*.
10. `==` checks *equality* as defined by the objects.

**Prediction question:** What if `other = items.copy()` instead? It
creates a new (shallow) list; subsequent `.append()` does not alter the
original list.

------------------------------------------------------------------------

# 7. Collections and Pythonic data processing

## 7.1 `dict`, `list`, and `set`

Create **`src/ai_python_bridge/collections_demo.py`**:

``` python
document = {
    "id": "doc-101",
    "title": "Incident Response",
    "tags": ["production", "operations"],
    "active": True,
}

print(document["title"])
print(document.get("owner", "unknown"))

tags = document["tags"]
tags.append("rag")

unique_tags = set(tags)
print(unique_tags)
```

**Line-by-line:**

1.  `{...}` creates a dictionary (mapping) with several key-value pairs.
2.  `"tags": [...]` stores a list inside the dictionary.
3.  `True` is Python's boolean literal (not Java `true`).
4.  `document["title"]` indexes a required key; missing keys raise
    `KeyError`.
5.  `document.get("owner", "unknown")` supplies a fallback when absent.
6.  `tags = document["tags"]` refers to the existing list.
7.  `.append("rag")` changes that list inside the dictionary.
8.  `set(tags)` creates a set with unique elements.
9.  Printing a set may show elements in varying order; do not write
    tests depending on that order.

  Java                      Python
  ------------------------- --------------------------------
  `List<String>`            `list[str]`
  `Map<String, Object>`     `dict[str, object]`
  `Set<String>`             `set[str]`
  `null`                    `None`
  `map.getOrDefault(...)`   `dictionary.get(key, default)`

## 7.2 List comprehensions vs Java Streams

``` python
scores = [0.91, 0.45, 0.83, 0.72]

high_scores = [
    score
    for score in scores
    if score >= 0.8
]

print(high_scores)
```

Output:

``` text
[0.91, 0.83]
```

**Line-by-line:**

1.  `scores` is a list of floating-point values.
2.  `high_scores = [` begins a list comprehension.
3.  `score` is the element to put in the output list.
4.  `for score in scores` iterates over input scores.
5.  `if score >= 0.8` filters results.
6.  `]` closes the expression; printing shows two retained values.

Similar Java:

``` java
List<Double> highScores = scores.stream()
    .filter(score -> score >= 0.8)
    .toList();
```

**Nuance:** Python list comprehensions eagerly produce lists. Java
Streams are lazy until a terminal operation. A Python *generator
expression* is a closer analogy to laziness:

``` python
squares_list = [n * n for n in range(5)]
squares_generator = (n * n for n in range(5))

print(squares_list)
print(list(squares_generator))
```

## 7.3 `None` and defaults

``` python
def get_model_name(config: dict[str, str]) -> str:
    name = config.get("model")

    if name is None:
        return "default-model"

    return name


print(get_model_name({}))
print(get_model_name({"model": "local-model"}))
```

**Line-by-line:**

1.  The function accepts a string-to-string dictionary.
2.  `.get("model")` returns the value or `None`.
3.  `is None` is the idiomatic missing-value check.
4.  The first `return` provides a default.
5.  The final `return` provides the configured value.
6.  The calls show both paths.

For production-sensitive settings, you might intentionally *reject* a
missing value rather than silently choose a default.

## 7.4 Exceptions

``` python
def parse_top_k(raw_value: str) -> int:
    try:
        top_k = int(raw_value)
    except ValueError as exc:
        raise ValueError("top_k must be an integer") from exc

    if top_k <= 0:
        raise ValueError("top_k must be positive")

    return top_k


print(parse_top_k("3"))
```

**Line-by-line:**

1.  `parse_top_k` returns an integer according to its annotation.
2.  `try:` protects code that may fail.
3.  `int(raw_value)` parses a numeric string or raises `ValueError`.
4.  `except ValueError as exc:` handles that specific failure.
5.  `raise ... from exc` produces a contextual error while preserving
    the original cause.
6.  `if top_k <= 0` validates the domain rule.
7.  `raise ValueError` rejects invalid values.
8.  `return top_k` returns the validated value.
9.  The final call prints `3`.

Unlike Java checked exceptions, Python exceptions need not be declared
in a method signature.

------------------------------------------------------------------------

# 8. Modules, packages, `__init__.py`, and `-m`

Think of a **module** as an importable Python source file. A **regular
package** is commonly a directory containing `__init__.py` and
additional modules.

Create **`src/ai_python_bridge/utils.py`**:

``` python
DEFAULT_TOP_K = 3


def normalize_text(text: str) -> str:
    return text.strip().lower()


def format_source(source: str, page: int) -> str:
    return f"{source} (page {page})"
```

**Line-by-line:**

1.  `DEFAULT_TOP_K` is a module-level constant by naming convention (not
    enforced).
2.  `normalize_text` takes and returns a string.
3.  `.strip()` removes surrounding whitespace; `.lower()` lowercases it.
4.  `format_source` accepts source text and an integer page number.
5.  The f-string formats a readable source label.

Create **`src/ai_python_bridge/module_demo.py`**:

``` python
from ai_python_bridge.utils import (
    DEFAULT_TOP_K,
    format_source,
    normalize_text,
)


def main() -> None:
    text = "  PRODUCTION INCIDENT  "
    print(normalize_text(text))
    print(format_source("runbook.md", 2))
    print(DEFAULT_TOP_K)


if __name__ == "__main__":
    main()
```

**Line-by-line:**

1.  `from ai_python_bridge.utils import (...)` imports three selected
    names from the `utils` module inside the package.
2.  `def main()` groups application execution.
3.  `text = ...` defines an input string.
4.  `normalize_text(text)` calls the helper from the other module.
5.  `format_source(...)` constructs a label.
6.  `print(DEFAULT_TOP_K)` reads the module constant.
7.  `if __name__ == "__main__":` guards the entry point.
8.  `main()` launches it.

Run:

``` powershell
uv run python -m ai_python_bridge.module_demo
```

Expected output:

``` text
production incident
runbook.md (page 2)
3
```

### Re-export from `__init__.py`

Edit **`src/ai_python_bridge/__init__.py`**:

``` python
from .utils import normalize_text

__all__ = ["normalize_text"]
```

-   `.utils` is a relative import of a sibling module.
-   The imported name becomes available from the package root.
-   `__all__` defines intended names for wildcard imports; it is **not**
    Java-style access control.

Test:

``` powershell
uv run python -c "from ai_python_bridge import normalize_text; print(normalize_text(' RAG '))"
```

Expected output: `rag`.

### Why `python -m`?

Prefer:

``` powershell
uv run python -m ai_python_bridge.module_demo
```

rather than relying on:

``` powershell
uv run python src/ai_python_bridge/module_demo.py
```

`-m` locates and executes a module through Python's import machinery.
Direct file execution uses different import-path behavior and can lead
to confusing package import failures.

**Java comparison:** A module is somewhat like a Java class/source
organization unit and a package is somewhat like a Java namespace, but
Python module top-level code can execute on import.

------------------------------------------------------------------------

# 9. Mini project: file-backed keyword retrieval

**Aim:** Reuse your knowledge of RAG while focusing entirely on Python
programming. We will read a file, turn each nonempty line into a
candidate passage, score passages by shared words, and return the best
results.

**This is NOT semantic embedding retrieval or a complete RAG pipeline.**
It is deliberately simple enough to teach Python data structures and
function contracts. A later session can replace the ranking
implementation without changing the larger application idea.

### Flow diagram

``` text
User question: str
         │
         ▼
load_chunks(Path) ───► list[str] of handbook passages
         │                           │
         └──────────┬────────────────┘
                    ▼
        retrieve(question, chunks, top_k)
                    │
       tokenize → set intersection
                    │
       score → sort → filter → slice
                    │
                    ▼
           list[tuple[int, str]]
                    │
                    ▼
             print selected passages

Later session only: retrieved passages → LLM prompt → generated answer
```

-   The handbook is the data source; lines act as already prepared
    chunks.
-   Tokenization here means splitting simple words, *not* an LLM
    tokenizer.
-   A score is the number of overlapping normalized words, *not* cosine
    similarity.
-   The result is ordinary Python data that another component could
    consume.
-   This local offline exercise requires no API key or network provider.

## 9.1 Create the input file

Create a folder **`data/`** in the project root and create
**`data/handbook.txt`**:

``` text
Production incidents must be reported to the on-call engineer.
A critical incident requires immediate escalation to the incident commander.
The rollback procedure must be approved before deploying a rollback.
Incident reports must include impact, timeline, root cause, and actions.
Service owners must review recurring production errors each week.
```

Each line is a distinct passage.

## 9.2 Implement loading and normalization

Create **`src/ai_python_bridge/retrieval.py`**:

``` python
from pathlib import Path


def load_chunks(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8")
    return [
        line.strip()
        for line in content.splitlines()
        if line.strip()
    ]


def tokenize(text: str) -> set[str]:
    return {
        word.strip(".,:;!?").lower()
        for word in text.split()
        if word.strip(".,:;!?")
    }
```

**Line-by-line explanation:**

1.  `from pathlib import Path` imports a standard-library filesystem
    path abstraction (compare Java NIO `Path`).
2.  `load_chunks(path: Path) -> list[str]` declares the file loader's
    input/output types.
3.  `path.read_text(encoding="utf-8")` loads a small text file into
    memory.
4.  `return [...]` starts a list comprehension.
5.  `line.strip()` removes whitespace around a line.
6.  `for line in content.splitlines()` iterates over file lines.
7.  `if line.strip()` removes empty/whitespace-only lines.
8.  `tokenize(...) -> set[str]` declares a helper returning unique
    words.
9.  `return {...}` is a set comprehension.
10. `word.strip(".,:;!?").lower()` removes specified edge punctuation
    and lowercases.
11. `for word in text.split()` splits on whitespace.
12. The condition omits pieces made only of those punctuation marks.

**Java analogy:**
`Files.readAllLines(path).stream().map(String::strip).filter(...).toList()`.

**Limitations:** This is not robust multilingual tokenization and does
not deal with stemming, full Unicode punctuation, or semantic
similarity.

## 9.3 Implement scoring and ranking

Append to the **same `retrieval.py`** file:

``` python
def retrieve(
    question: str,
    chunks: list[str],
    top_k: int = 2,
) -> list[tuple[int, str]]:
    if top_k <= 0:
        raise ValueError("top_k must be positive")

    question_words = tokenize(question)

    scored = [
        (len(question_words & tokenize(chunk)), chunk)
        for chunk in chunks
    ]

    ranked = sorted(
        scored,
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        (score, chunk)
        for score, chunk in ranked
        if score > 0
    ][:top_k]
```

**Line-by-line explanation:**

1.  `retrieve(...)` takes the user question and passages.
2.  `top_k: int = 2` defines a default argument.
3.  `-> list[tuple[int, str]]` describes a list of `(score, passage)`
    pairs.
4.  `if top_k <= 0` validates a parameter.
5.  `raise ValueError(...)` rejects invalid input.
6.  `question_words = tokenize(question)` gets normalized query terms.
7.  `scored = [...]` constructs scored passage pairs.
8.  `question_words & tokenize(chunk)` is **set intersection**.
9.  `len(...)` counts shared terms.
10. `(score, chunk)` is a Python tuple.
11. `for chunk in chunks` scores every passage.
12. `sorted(...)` returns a new sorted list.
13. `key=lambda item: item[0]` sorts by tuple element zero, the score.
14. `reverse=True` means descending scores.
15. The final comprehension unpacks each tuple into `score, chunk`.
16. `if score > 0` omits zero-overlap results.
17. `[:top_k]` selects the first at most `top_k` results.

### Similar Java shape

``` java
record Hit(int score, String chunk) {}

List<Hit> hits = chunks.stream()
    .map(chunk -> new Hit(
        overlapCount(questionWords, tokenize(chunk)),
        chunk
    ))
    .filter(hit -> hit.score() > 0)
    .sorted(Comparator.comparingInt(Hit::score).reversed())
    .limit(topK)
    .toList();
```

`overlapCount` and `tokenize` here are assumed Java helper methods. The
code illustrates the pipeline rather than supplying a complete Java
program.

## 9.4 Add the application entry point

Create **`src/ai_python_bridge/main.py`**:

``` python
from pathlib import Path

from ai_python_bridge.retrieval import load_chunks, retrieve


def main() -> None:
    question = "How do we escalate a critical incident?"
    path = Path("data/handbook.txt")

    try:
        chunks = load_chunks(path)
        results = retrieve(question, chunks, top_k=2)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Application error: {exc}")
        return

    print(f"Question: {question}")

    for index, (score, chunk) in enumerate(results, start=1):
        print(f"{index}. Score={score} | {chunk}")


if __name__ == "__main__":
    main()
```

**Line-by-line explanation:**

1.  `Path` imports filesystem path support.
2.  The second import brings in two functions from our package.
3.  `main()` marks the application entry point.
4.  `question` defines user input.
5.  `Path("data/handbook.txt")` is relative to the terminal's current
    working directory.
6.  `try:` begins error handling.
7.  `load_chunks(path)` reads the file.
8.  `retrieve(...)` selects top matching passages.
9.  `except (FileNotFoundError, ValueError) as exc:` catches two
    expected failure types.
10. `print(...)` reports the error without a raw traceback.
11. `return` stops `main` on failure.
12. `print(f"Question: ...")` displays the input.
13. `enumerate(results, start=1)` produces 1-based result numbers.
14. `for index, (score, chunk)` uses tuple unpacking.
15. The final `print` formats each result.
16. The `__main__` guard invokes `main()` only for entry-point
    execution.

Run:

``` powershell
uv run python -m ai_python_bridge.main
```

Expected output:

``` text
Question: How do we escalate a critical incident?
1. Score=3 | A critical incident requires immediate escalation to the incident commander.
2. Score=1 | Incident reports must include impact, timeline, root cause, and actions.
```

**Critical observation:** Result 2 matches a word but is not a good
answer to the question. The function performed its *defined algorithm*
correctly, yet its *retrieval quality* is limited. This is the
distinction between software correctness and AI/retrieval relevance.

------------------------------------------------------------------------

# 10. Test the retriever with pytest

`pytest` was installed earlier using `uv add --dev pytest`. Create a
**`tests/`** directory at the project root and add
**`tests/test_retrieval.py`**:

``` python
import pytest

from ai_python_bridge.retrieval import retrieve, tokenize


def test_tokenize_normalizes_case() -> None:
    assert tokenize("RAG rag!") == {"rag"}


def test_retrieve_ranks_relevant_chunks() -> None:
    chunks = [
        "Deployments require approval",
        "Critical incidents require escalation",
    ]

    results = retrieve("critical escalation", chunks)

    assert len(results) == 1
    assert results[0][1] == chunks[1]


def test_retrieve_rejects_invalid_top_k() -> None:
    with pytest.raises(ValueError):
        retrieve("incident", ["incident guide"], top_k=0)
```

**Line-by-line explanation:**

1.  `import pytest` brings in the test framework.
2.  The second import loads production functions.
3.  Functions named `test_*` are discovered by pytest.
4.  The first `assert` checks lowercasing and punctuation trimming.
5.  The second test prepares two input passages.
6.  `retrieve(...)` invokes production logic.
7.  `assert len(results) == 1` checks a single passage remains after
    filtering.
8.  `results[0][1]` accesses the passage from the first `(score, chunk)`
    tuple.
9.  `with pytest.raises(ValueError):` asserts the enclosed call raises
    an error.
10. `top_k=0` verifies parameter validation.

Run:

``` powershell
uv run pytest -q
```

Expected summary:

``` text
3 passed
```

`pytest` provides equivalent intent to JUnit tests but uses function
naming, ordinary Python asserts, and fixtures rather than requiring Java
test classes.

------------------------------------------------------------------------

# 11. Guided quiz and troubleshooting

Try answering before reading the answers.

### Q1. Why might `python --version` show 3.13 but `uv run python --version` show 3.12?

Because PowerShell's normal Python command selection and uv's project
environment selection may use different interpreters. Confirm with
`sys.executable`.

### Q2. Does `uv python install 3.12` uninstall Python 3.13?

No. They can coexist.

### Q3. What is the difference between `pyproject.toml`, `uv.lock`, and `.venv`?

Requirements/configuration vs resolved dependency information vs the
local environment holding interpreter/packages.

### Q4. Why is `uv run python -m pip --version` allowed to fail?

A uv environment doesn't necessarily include pip. `uv` can resolve and
install dependencies without it.

### Q5. Is `name: str` enforced by Python?

No, not automatically at runtime. It documents the expected type and is
useful to static tooling.

### Q6. Why might `other.append(3)` change `items`?

If `other = items`, both names refer to the same mutable list.

### Q7. `==` or `is`: which checks `None`?

Use `is None` for the singleton `None` object.

### Q8. What does `if score > 0` do in the final comprehension?

Filters passages with no word overlap.

### Q9. What does `[:top_k]` do?

Returns at most the first `top_k` entries of a sequence.

### Q10. What is `__init__.py` for?

It makes a directory a regular Python package and may initialize or
re-export package API names. It may be empty.

### Q11. Why execute with `python -m ai_python_bridge.main`?

To have Python resolve and execute the module through its package import
machinery.

### Q12. Does a passing test prove the retriever is semantically accurate?

No. A unit test can prove the word-overlap implementation behaves as
specified; retrieval-quality evaluation is a separate concern.

## Debugging drill

Change this import in `main.py`:

``` python
from ai_python_bridge.retreival import retrieve
```

What happens? The module name is misspelled: Python cannot find it.
Correct `retreival` → `retrieval` (and restore the original imports if
you replaced them).

Next change the path temporarily to:

``` python
path = Path("data/missing-handbook.txt")
```

Run the app and observe the `FileNotFoundError` being caught by the
application. Restore the original path afterward.

------------------------------------------------------------------------

# 12. Self-paced exercises

Do these after running all previous examples. Avoid copying the solution
immediately; predict, run, inspect, and test.

## Exercise A --- Environment detective

1.  From inside the project, run `python --version` and
    `uv run python --version`.
2.  Inspect both `sys.executable` paths.
3.  Open `.python-version`.
4.  Inspect the `dev` group in `pyproject.toml`.
5.  Run `uv tree`, and identify which package is a direct dependency and
    which dependencies are transitive.
6.  Explain, in your own words, why `.venv` should not be committed.

**Success:** You can point to the active interpreter and explain how
dependencies get into its environment.

## Exercise B --- Python reference behavior

Predict the output, then execute in a new scratch module:

``` python
values = [1, 2, 3]
copy_a = values
copy_b = values.copy()

copy_a.append(4)

print(values)
print(copy_b)
```

**Expected:**

``` text
[1, 2, 3, 4]
[1, 2, 3]
```

Explain why. Also note that `.copy()` is **shallow**, not a recursive
deep copy.

## Exercise C --- Extend the retriever

Change the function signature to support a minimum score:

``` python
def retrieve(
    question: str,
    chunks: list[str],
    top_k: int = 2,
    min_score: int = 1,
) -> list[tuple[int, str]]:
```

Requirements:

1.  Reject negative `min_score` values with `ValueError`.
2.  Replace the hard-coded `score > 0` check with a filter based on
    `min_score`.
3.  Add a pytest test showing that `min_score=2` excludes a passage
    matching only one word.
4.  Run `uv run pytest -q`.

**Think before coding:** If `min_score=0` is permitted, should a
zero-overlap passage be included? With a literal `score >= min_score`
filter, yes. Decide whether that contract is acceptable and describe it
in a comment or test.

**Solution outline (look only after trying):**

``` python
if min_score < 0:
    raise ValueError("min_score must be non-negative")
```

In the final comprehension use:

``` python
if score >= min_score
```

Add a test with passages of overlap 1 and 2, and assert only the latter
remains when `min_score=2`.

------------------------------------------------------------------------

# 13. A compact architecture reflection (from the course workbook)

This is a **short companion reflection**, not a new AI theory module.
Your supplied `assignment.md` asks for a roughly two-page
`genai-design-brief.md`, with: problem/users; architecture choice;
simpler alternative rejected; inputs and excluded sensitive data; model
route; two failure modes including one non-model failure; quality and
operational evaluation; human review/control; and a box-and-arrow
sketch.

For this Python session, you may begin with:

``` markdown
# GenAI Design Brief — Incident Response Assistant

## Problem and users
On-call engineers need evidence-based guidance about incidents.

## Proposed architecture
Standard RAG over approved runbooks (future implementation).

## Why
Internal procedures change. A direct model may not know them;
an agent would add unnecessary autonomy.

## Current Python exercise
The keyword retriever demonstrates file loading, passage ranking,
and a retrieval boundary. It is not yet an embedding or LLM application.
```

Then complete the rest independently using the **original assignment
instructions**. Do not submit credentials or `.env` files.

------------------------------------------------------------------------

# 14. Final project tree and commands

Your completed local project should resemble:

``` text
ai-python-bridge/
├── .python-version
├── .gitignore
├── .venv/                        # local, ignored by git
├── pyproject.toml
├── uv.lock
├── README.md
├── data/
│   └── handbook.txt
├── src/
│   └── ai_python_bridge/
│       ├── __init__.py
│       ├── syntax_demo.py
│       ├── control_flow.py
│       ├── identity_demo.py
│       ├── collections_demo.py
│       ├── utils.py
│       ├── module_demo.py
│       ├── retrieval.py
│       └── main.py
├── tests/
│   └── test_retrieval.py
└── genai-design-brief.md         # optional companion brief
```

Use this final verification sequence:

``` powershell
uv run python --version
uv run python -m ai_python_bridge.syntax_demo
uv run python -m ai_python_bridge.control_flow
uv run python -m ai_python_bridge.module_demo
uv run python -m ai_python_bridge.main
uv run pytest -q
uv tree
uv sync --locked
```

`uv sync --locked` ensures the lockfile is up to date rather than
silently updating it; the environment is synced from the project's
resolved dependencies.

## Exit checklist

-   [ ] I can explain why `python` and `uv run python` may select
    different Python versions.
-   [ ] I can locate the Python executable inside `.venv`.
-   [ ] I know what `.python-version`, `pyproject.toml`, `uv.lock`, and
    `.venv` do.
-   [ ] I can use `uv add`, `uv remove`, `uv tree`, `uv sync`, and
    `uv run`.
-   [ ] I can explain type annotations, indentation, `None`, lists,
    dicts, sets, and tuples.
-   [ ] I can explain a comprehension, a generator expression, and a
    lambda.
-   [ ] I can create modules and a package with `__init__.py`.
-   [ ] I can run a package module using `python -m`.
-   [ ] I can read files with `pathlib`, handle exceptions, and write a
    small retriever.
-   [ ] I can run and modify `pytest` tests.
-   [ ] I understand why a correctly coded retriever can still return a
    low-quality result.

## Official reference links

-   [uv getting started](https://docs.astral.sh/uv/getting-started/)
-   [Installing and managing Python with
    uv](https://docs.astral.sh/uv/guides/install-python/)
-   [Creating uv
    projects](https://docs.astral.sh/uv/concepts/projects/init/)
-   [Managing
    dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/)
-   [Running commands](https://docs.astral.sh/uv/concepts/projects/run/)
-   [Locking and
    syncing](https://docs.astral.sh/uv/concepts/projects/sync/)
-   [Python packaging:
    `pyproject.toml`](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
-   [Python tutorial](https://docs.python.org/3/tutorial/)
-   [pytest documentation](https://docs.pytest.org/)

------------------------------------------------------------------------

**Next learning stage (not covered here):** Validated data models with
Pydantic, service APIs with FastAPI, asynchronous I/O with `asyncio`, a
UI with Streamlit or Gradio, and a proper LangChain-backed RAG
application. This guide establishes the Python foundation for those
subjects.

------------------------------------------------------------------------

# 4A. Deeper uv concepts: project types, scripts, builds, and team workflows

This section expands the uv topics that commonly cause confusion when
moving from Java/Maven to Python. It is designed as a practical
follow-on to Sections 2--4.

## 4A.1 `uv init`: what does `--package` mean?

A Python project can be organized as an application, a package, or a
library. These are related but not identical ideas.

-   An **application** is something you primarily want to run.
-   A **package** is importable Python code that can be installed into
    an environment.
-   A **library** is a package intended for other projects to consume.

For a packaged project, uv commonly creates a `src/` layout, an
importable package directory, and build configuration.

Example:

``` powershell
uv init --package --python 3.12 ai-bridge
```

The `--package` option explicitly asks for a packaged project.

To request an unpackaged application layout:

``` powershell
uv init --no-package ai-bridge-app
```

Depending on the installed uv version, the default created by `uv init`
may already be a packaged project. Therefore, do not assume that
omitting `--package` must produce a different layout. Check the
generated files and your uv version:

``` powershell
uv --version
Get-ChildItem
Get-Content .\pyproject.toml
```

**Learning point:** `--package` expresses your intention. The generated
structure depends on the uv version and the selected project mode.

## 4A.2 `.python-version` versus `requires-python`

These two settings are related, but they answer different questions.

A `.python-version` file might contain:

``` text
3.12
```

This tells uv which Python version to prefer for the project.

The project metadata might contain:

``` toml
[project]
requires-python = ">=3.12"
```

This declares which Python versions the project supports. It is a
compatibility range, not an exact interpreter pin.

For example:

  ------------------------------------------------------------------------
  Setting                              Meaning
  ------------------------------------ -----------------------------------
  `.python-version` = `3.12`           Prefer Python 3.12 for this project

  `requires-python = ">=3.12"`         Python 3.12 and later versions are
                                       allowed by this declaration

  `requires-python = ">=3.12,<3.13"`   Python 3.12 versions are allowed;
                                       Python 3.13 is excluded
  ------------------------------------------------------------------------

A project can prefer Python 3.12 while declaring that it supports later
versions too.

**Important:** A declared compatibility range is a promise made by the
project. Do not widen it unless your code and dependencies have actually
been tested on those versions.

## 4A.3 What if a teammate has a different Python version?

Suppose the repository contains:

`.python-version`

``` text
3.12
```

`pyproject.toml`

``` toml
[project]
requires-python = ">=3.12"
```

A teammate clones the repository and has only Python 3.11 installed.

When they run:

``` powershell
uv sync
```

uv needs an interpreter that satisfies `requires-python`. Python 3.11
does not satisfy `>=3.12`.

By default, uv can download a compatible managed Python version when
needed. Therefore, the teammate may not see an error: uv can obtain
Python 3.12 and create the project's `.venv` with it.

If automatic downloads are disabled or the required interpreter cannot
be obtained, uv reports that it cannot find a compatible interpreter.
The exact error wording can vary by uv version and configuration.

A teammate can also explicitly install the requested interpreter:

``` powershell
uv python install 3.12
uv sync
```

After syncing, verify the interpreter actually used by the project:

``` powershell
uv run python --version
uv run python -c "import sys; print(sys.executable)"
```

The executable path should normally point into the project environment,
for example:

``` text
C:\projects\ai-bridge\.venv\Scripts\python.exe
```

### What if the settings conflict?

For example:

`.python-version`

``` text
3.12
```

`pyproject.toml`

``` toml
[project]
requires-python = ">=3.13"
```

Python 3.12 is the preferred version, but it does not satisfy the
project's minimum requirement. uv cannot successfully create a project
environment using Python 3.12 for this project. Correct the
configuration so the preferred interpreter and compatibility requirement
agree.

## 4A.4 What is `[project.scripts]`?

Consider this configuration:

``` toml
[project.scripts]
ai-bridge = "ai_bridge:main"
```

This defines an installed command-line entry point.

The general format is:

``` text
command-name = "python_module_or_package:function_name"
```

In this example:

-   `ai-bridge` is the command users type.
-   `ai_bridge` is the Python import module or package.
-   `main` is the function that should be called.

For example, the package might contain:

``` text
src/
└── ai_bridge/
    └── __init__.py
```

And `src/ai_bridge/__init__.py` might contain:

``` python
def main() -> None:
    print("Hello from AI Bridge!")
```

After the project is installed into its environment, the entry-point
command can be run with:

``` powershell
uv run ai-bridge
```

The command name can contain hyphens even though Python import names use
underscores in this example.

**Java comparison:** This is similar in purpose to providing a
convenient application entry point, but Python packaging creates a
command-line launcher that calls the configured function.

The function must exist at the specified import path. If the package or
function name is wrong, the launcher may be created but fail when
executed.

## 4A.5 What is `[build-system]`?

Consider:

``` toml
[build-system]
requires = ["uv_build>=0.13.1,<0.14.0"]
build-backend = "uv_build"
```

This section describes how the project is built into distributable
Python package artifacts.

### `requires`

``` toml
requires = ["uv_build>=0.13.1,<0.14.0"]
```

This declares the build-time requirement:

-   `uv_build` is the build backend package.
-   `>=0.13.1` means version 0.13.1 or newer.
-   `<0.14.0` excludes version 0.14.0 and later.

This is a version range for the build tool. It is not a requirement that
the project's users install uv CLI version 0.13.1.

### `build-backend`

``` toml
build-backend = "uv_build"
```

This identifies the backend that performs the build.

A useful distinction:

-   `requires` says which build requirements must be available.
-   `build-backend` identifies the backend entry point used to perform
    the build.

**Java comparison:** This is broadly comparable to specifying the build
tooling used to create a JAR, although Python's packaging standards and
build-backend mechanism are different from Maven or Gradle.

The exact backend and version range generated by `uv init` can change
across uv versions. Treat the generated configuration as project
configuration; do not casually edit it without understanding the effect.

## 4A.6 What does `uv build` do?

Run:

``` powershell
uv build
```

For a buildable package project, uv creates distribution artifacts in
`dist/`, commonly:

``` text
dist/
├── ai_bridge-0.1.0.tar.gz
└── ai_bridge-0.1.0-py3-none-any.whl
```

These are two distribution formats:

-   **Source distribution (`.tar.gz`)**: a source package that can be
    used to build/install the project.
-   **Wheel (`.whl`)**: a built Python distribution designed for
    installation.

A successful `uv build` means the artifacts were built. It does **not**
mean the project has been installed into the current `.venv`, and it
does not by itself make a command-line script available in the current
shell.

To install/synchronize the local project in its development environment,
use:

``` powershell
uv sync
```

Then run an installed script through the project environment:

``` powershell
uv run ai-bridge
```

For a normal packaged project, `uv sync` installs the project in
editable mode by default. This is why the command can become available
after syncing.

## 4A.7 Why did PowerShell say the command was not recognized?

Suppose `pyproject.toml` contains:

``` toml
[project.scripts]
ai-bridge = "ai_bridge:main"
```

You run:

``` powershell
uv build
ai-bridge
```

The build can succeed, while PowerShell reports that `ai-bridge` is not
recognized.

These commands do different jobs:

  -----------------------------------------------------------------------
  Command                             Responsibility
  ----------------------------------- -----------------------------------
  `uv build`                          Build distribution files in `dist/`

  `uv sync`                           Synchronize the project environment
                                      and install the project

  `uv run ai-bridge`                  Run the command in the project's
                                      environment
  -----------------------------------------------------------------------

PowerShell does not automatically search every project's `.venv\Scripts`
directory. `uv run` runs the command with the project environment
available.

A practical sequence is:

``` powershell
uv sync
uv run ai-bridge
```

If the command is found but fails with an import or attribute error,
check that the module and function named in `[project.scripts]` really
exist.

## 4A.8 What is `uv.lock`?

Think of `pyproject.toml` as the project's dependency requirements and
`uv.lock` as the record of the resolved dependency graph.

For example, `pyproject.toml` might say:

``` toml
[project]
dependencies = [
    "httpx>=0.27"
]
```

This is a range. It does not name one exact HTTPX version.

The lockfile records the selected version and the resolved transitive
dependencies needed by the project, along with package source and
distribution metadata.

A simplified conceptual example:

``` text
httpx       0.28.1
httpcore    1.0.9
anyio       4.10.0
```

These versions are illustrative; inspect your own `uv.lock` for the
actual resolution.

### Why commit `uv.lock`?

For an application project, commit both:

-   `pyproject.toml`
-   `uv.lock`

This allows teammates and CI systems to use the same recorded dependency
resolution, subject to platform and environment markers.

Do not commit `.venv/`. It is a local environment that can be recreated.

A useful Git checklist:

  File/folder           Commit?
  --------------------- ---------------------------------------------------------
  `pyproject.toml`      Yes
  `uv.lock`             Yes
  `.python-version`     Usually yes
  `src/` and `tests/`   Yes
  `.gitignore`          Yes
  `.venv/`              No
  `__pycache__/`        No
  `dist/`               Usually no for ordinary application source repositories

## 4A.9 What does `uv sync` do for a teammate?

A typical workflow:

### Developer A

Add a dependency:

``` powershell
uv add httpx
```

uv updates the project dependency declaration and lockfile, and normally
synchronizes the environment.

Commit the relevant files:

``` powershell
git add pyproject.toml uv.lock .python-version
git commit -m "Add httpx dependency"
git push
```

### Developer B

Clone the repository:

``` powershell
git clone <repository-url>
cd <project-folder>
```

Synchronize the environment:

``` powershell
uv sync
```

uv reads the project metadata and lockfile, selects a compatible Python
interpreter, creates or updates `.venv`, and installs the project's
dependencies. For a packaged project, it also installs the project
itself in editable mode by default.

To run a project command:

``` powershell
uv run ai-bridge
```

### Does this guarantee identical environments?

It makes dependency resolution reproducible, but it does not guarantee
that every machine is identical. Operating system, architecture, Python
version, environment markers, and platform-specific packages can affect
what is installed.

## 4A.10 What does `--locked` mean?

Compare:

``` powershell
uv sync
```

with:

``` powershell
uv sync --locked
```

-   `uv sync` can update the lockfile if it is missing or out of date,
    then synchronize the environment.
-   `uv sync --locked` checks that the lockfile is already up to date.
    If it needs an update, uv reports an error instead of modifying the
    lockfile.

This is useful for CI/CD and team workflows because it catches a
forgotten lockfile update.

**Important:** `--locked` protects the lockfile from being updated by
that command. It does not mean that uv will never install, remove, or
update packages in `.venv`. The environment is still synchronized to the
locked resolution.

There is also a related option:

``` powershell
uv sync --frozen
```

`--frozen` uses the existing lockfile without checking whether it is up
to date with the project metadata. It is not a substitute for the
consistency check provided by `--locked`.

## 4A.11 A practical team exercise

Work through this exercise in two local project copies or with a
teammate.

1.  In the first project copy, run:

    ``` powershell
    uv add httpx
    ```

2.  Inspect the dependency declaration:

    ``` powershell
    Get-Content .\pyproject.toml
    ```

3.  Inspect the lockfile:

    ``` powershell
    Get-Content .\uv.lock
    ```

4.  Commit and push `pyproject.toml` and `uv.lock`.

5.  In the second project copy, pull the changes and run:

    ``` powershell
    uv sync --locked
    ```

6.  Inspect the installed dependency tree:

    ``` powershell
    uv tree
    ```

7.  Verify the interpreter:

    ``` powershell
    uv run python --version
    uv run python -c "import sys; print(sys.executable)"
    ```

**Success criteria:** You can explain which file declares the
requirement, which file records the resolution, and which directory
contains the installed environment.

## 4A.12 Troubleshooting reference

  -------------------------------------------------------------------------------------
  Symptom                            Likely explanation      What to check or do
  ---------------------------------- ----------------------- --------------------------
  `uv python install 3.12` says an   A file at uv's target   Inspect the executable and
  executable already exists and is   executable path already its owner before
  not managed by uv                  exists                  considering `--force`

  `uv sync` cannot find a compatible No usable compatible    Check `requires-python`,
  interpreter                        interpreter was found,  `.python-version`,
                                     and uv could not obtain download settings, and run
                                     one                     `uv python install 3.12`
                                                             if appropriate

  `uv sync --locked` reports that    `pyproject.toml` and    Run `uv lock`, review the
  the lockfile needs updating        `uv.lock` are out of    change, and commit the
                                     sync                    updated lockfile

  PowerShell says a project script   The project may not be  Run `uv sync`, then
  is not recognized                  installed in the        `uv run <script-name>`
                                     environment, or the     
                                     command is not being    
                                     run through that        
                                     environment             

  A script starts but reports a      The `[project.scripts]` Verify the module/package
  missing function or module         target may be incorrect and function named in the
                                                             entry point

  `uv run python -m pip --version`   pip is not necessarily  This is not automatically
  says no module named pip           installed in a uv       an environment failure;
                                     environment             ordinary uv workflows do
                                                             not require pip
  -------------------------------------------------------------------------------------

### Investigating an existing Python executable before using `--force`

If uv reports that an executable already exists but is not managed by
uv, do not immediately overwrite it.

On Windows PowerShell, inspect it first:

``` powershell
& "$env:USERPROFILE\.local\bin\python3.12.exe" --version
& "$env:USERPROFILE\.local\bin\python3.12.exe" -c "import sys; print(sys.executable); print(sys.prefix)"
uv python list --only-installed
```

`--force` permits uv to replace the conflicting executable. That can
disrupt another tool or installation that relies on the existing file.
Use it only after understanding what the existing executable is and
deciding that replacement is safe.

------------------------------------------------------------------------
