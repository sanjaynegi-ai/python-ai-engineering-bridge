# VS Code for This Course

Any editor works, but the course's instructions assume [VS Code](https://code.visualstudio.com/). If you use PyCharm or another IDE daily, use it, and translate the editor-specific steps.

## Extensions

Install these from the Extensions view (`Ctrl+Shift+X`, or `Cmd+Shift+X` on macOS):

| Extension | Publisher | What it gives you |
|---|---|---|
| **Python** | Microsoft | Interpreter selection, running and debugging Python, test discovery. It installs **Pylance** (code intelligence) with it |
| **Jupyter** | Microsoft | Notebooks inside VS Code |
| **Ruff** | Astral Software | Lint warnings as you type, and formatting on save |

## Selecting the interpreter

VS Code needs to know which Python environment a folder uses. Open the folder (the course repository, or one of your projects), then:

1. Open the Command Palette (`Ctrl+Shift+P`, or `Cmd+Shift+P`).
2. Run **Python: Select Interpreter**.
3. Choose the one inside the folder's `.venv`.

If `.venv` isn't listed, run `uv sync` in that folder first, then try again. Choosing the wrong interpreter is the most common cause of "module not found" errors in the editor while `uv run` works fine in the terminal.

For notebooks, the kernel is chosen separately: click **Select Kernel** at the top right of the notebook, then **Python Environments**, then `.venv`.

## Formatting and linting with Ruff

To format Python files when you save, add this to your user or workspace settings (`Preferences: Open User Settings (JSON)`):

```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

The Ruff extension reads each project's `[tool.ruff]` settings from `pyproject.toml`, so the editor and `uv run ruff check .` agree.

## Running tests

Open the **Testing** view (the flask icon). The first time, VS Code asks how to discover tests: choose **pytest**, then the folder. Tests then appear in a tree, and you can run or debug one at a time. Your workbooks give the same tests as `uv run pytest` commands; both run the same tests.

## Debugging

Set a breakpoint by clicking left of a line number, then:

- in a test: right-click its green arrow, and choose **Debug Test**;
- in a script: **Run → Start Debugging** (`F5`), and choose **Python File**;
- in a notebook cell: the cell's dropdown menu, **Debug Cell**.

[`debugging-python.md`](debugging-python.md) covers the debugger, `breakpoint()` and reading tracebacks.

## Terminals

Use VS Code's integrated terminal (`` Ctrl+` ``). It opens in the current folder. On Windows, PowerShell is the default; every course command is given for PowerShell where it differs from Bash.
