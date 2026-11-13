# Getting Started

Set up everything **before Session 01**. It takes about 30 minutes, longer on a slow connection. If you get stuck, see [`troubleshooting.md`](troubleshooting.md), and bring the exact error message to your instructor.

## 1. Install uv

[uv](https://docs.astral.sh/uv/) installs Python, creates project environments and manages dependencies. It's the only Python tool you need to install yourself.

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Both commands download and run an install script from astral.sh. If you prefer to read it first, open the URL in a browser. Alternatives: `brew install uv` on macOS, or `winget install --id=astral-sh.uv -e` on Windows.

Open a **new** terminal, so it picks up the new `PATH`, and check:

```bash
uv --version     # 0.13 or newer
```

## 2. Install Python 3.13

```bash
uv python install 3.13
```

You don't need Python from python.org, or `pip`, for this course. uv keeps its own Python installations, so this doesn't change anything else on your machine.

## 3. Install Git and VS Code

- **Git:** `git --version` should print a version. If not, install it from [git-scm.com](https://git-scm.com/downloads).
- **VS Code**, with the **Python**, **Jupyter** and **Ruff** extensions. See [`setup-vscode.md`](setup-vscode.md).

## 4. Clone the course repository and create its environment

Copy the repository URL from the **Code** button on its GitHub page. Then:

```bash
git clone <the URL you copied>
cd python-ai-engineering-bridge
uv sync
```

`uv sync` creates a `.venv` folder with every package the notebooks need, at exactly the versions in `uv.lock`. Check it:

```bash
uv run python --version                        # Python 3.13.x
uv run python scripts/validate_notebooks.py sessions/session-01
```

The second command runs Session 01's notebooks from a fresh kernel. It should end with `Failed: 0`.

## 5. Open the first notebook

1. In VS Code: **File → Open Folder**, and choose `python-ai-engineering-bridge`.
2. Open `sessions/session-01/notebooks/01-concepts.ipynb`.
3. Click **Select Kernel** (top right) → **Python Environments** → the one in `.venv`.
4. Run the first code cell.

[`using-jupyter.md`](using-jupyter.md) explains notebooks in more detail, including JupyterLab.

## 6. Create a folder for your own work

Your assignments live **outside** the course repository, so that `git pull` never conflicts with your work:

```bash
# macOS / Linux / Git Bash
mkdir ~/skillup

# PowerShell
mkdir ~\skillup
```

Each workbook tells you what to create there.

## 7. Optional: an LLM API key

You need one only from Session 09, and every test also runs without one. Session 01, Part 8 explains the choices, and [`api-key-security.md`](api-key-security.md) explains how to keep a key safe. If your company has to approve a provider, start now.

## Keeping up to date

At the start of each weekend, pull the new material:

```bash
cd python-ai-engineering-bridge
git pull
uv sync
```

`uv sync` adds any packages that new sessions need. Don't edit files inside the course repository: copy them to your own folder first. Otherwise `git pull` will report conflicts.
