# Using `venv` and pip Instead of uv

The course uses uv throughout, and that's what we recommend. If your machine can't run uv (some locked-down corporate laptops), you can follow the course with Python's built-in `venv` and pip. This page translates the course's commands.

Use one approach consistently. Mixing uv and pip in the same project leads to environments nobody can reproduce.

## What you give up

- **Lockfiles for your projects.** pip doesn't use `uv.lock`, so `pip install` picks the newest versions that satisfy each project's constraints, which may differ from the versions the course tested. For the course repository itself, `requirements.txt` pins exact versions, so the notebooks are unaffected.
- **Automatic Python installation.** You install Python 3.13 yourself.
- **`uv run`.** You activate the environment instead, and must remember to.

## 1. Install Python 3.13

From [python.org](https://www.python.org/downloads/), or your operating system's package manager. Check:

```bash
python3.13 --version        # macOS / Linux
py -3.13 --version          # Windows
```

## 2. The course repository

From the repository root:

```bash
# macOS / Linux
python3.13 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
```

Your prompt now shows `(.venv)`. Then install the pinned course packages:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` is generated from `uv.lock`, so you get exactly the tested versions. When `git pull` brings a new `requirements.txt`, run the install command again.

If PowerShell refuses to run `Activate.ps1`, allow local scripts for your user once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## 3. Your projects

Workbooks tell you to copy a starter, then run `uv sync`. With pip, from the project folder:

```bash
python3.13 -m venv .venv            # Windows: py -3.13 -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e . --group dev
```

`-e .` installs the project itself in *editable* mode, so changes to your code take effect without reinstalling, and installs its dependencies. `--group dev` adds the `dev` dependency group (pytest, Ruff ...). It needs pip 25.1 or newer, which is why pip is upgraded first.

## Translating workbook commands

With the environment **activated**:

| Workbook says | You run |
|---|---|
| `uv sync` | `python -m pip install -e . --group dev` (again, after dependencies change) |
| `uv run pytest` | `python -m pytest` |
| `uv run ruff check .` | `python -m ruff check .` |
| `uv run python main.py` | `python main.py` |
| `uv run incident-report` | `incident-report` |
| `uv add httpx` | Add `"httpx"` to `dependencies` in `pyproject.toml`, then `python -m pip install -e . --group dev` |
| `uv add --dev pytest-asyncio` | Add it to the `dev` group in `pyproject.toml`, then install as above |
| `uv lock --check` | No equivalent. Skip it, and say so in your notes |

## Notebooks

In VS Code, select the kernel from `.venv` in the course repository, exactly as with uv. In JupyterLab, start it from the activated environment: `jupyter lab`.

## Further reading

- [`venv` documentation](https://docs.python.org/3.13/library/venv.html)
- [Installing packages with pip](https://pip.pypa.io/en/stable/user_guide/)
