# Using the Course Notebooks

Each session's notebooks explain the concepts, with runnable examples. You can use them in VS Code or in JupyterLab.

## Opening a notebook

**In VS Code** (recommended): open the course repository folder, open a `.ipynb` file, and choose the `.venv` kernel with **Select Kernel → Python Environments**. See [`setup-vscode.md`](setup-vscode.md).

**In JupyterLab**: from the repository root, run

```bash
uv run jupyter lab
```

It opens in your browser, already using the course environment.

## Running cells

- Run cells **from the top, in order**. Later cells use names that earlier cells define.
- `Shift+Enter` runs a cell and moves to the next.
- To start again from a clean state, use **Restart** and then **Run All**. If a notebook behaves strangely after you've experimented, that's the first thing to try.
- Cells that demonstrate an error catch it and print it, so **Run All** goes through the whole notebook.

The **Modify** prompts ask you to change code and run it again. Do: that's where most of the learning happens. To get the original back, use `git checkout -- path/to/notebook.ipynb` (this discards *all* your changes to that notebook), or keep your experiments in a copy.

## Answers in the quizzes

Quiz answers are hidden in collapsible **Show answer** sections. Write down your answer first, then open it. Run the question's code cell, if there is one, before you look.

## Notebooks that can call paid APIs

From Session 09, some notebooks can call an LLM provider. They do so **only if you opt in**: a variable near the top, such as `RUN_LIVE_CALLS = False`, controls it. By default they use example replies, so running them costs nothing and needs no key. Set it to `True` only when you have a key in `.env` and want to see a real model's answers.

## Checking the notebooks

To confirm that every notebook runs from a fresh kernel in your environment:

```bash
uv run python scripts/validate_notebooks.py
uv run python scripts/validate_notebooks.py sessions/session-03     # one session
```

## Common problems

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` in a notebook | The wrong kernel. Select `.venv` in the course repository, and run `uv sync` if packages are missing |
| No `.venv` kernel in the list | Run `uv sync` in the repository root, then reload VS Code (`Developer: Reload Window`) |
| A cell waits forever | The kernel may be busy or stuck: **Interrupt**, then **Restart** |
| `NameError` for something defined earlier | You skipped or restarted past an earlier cell: **Restart** and **Run All** |
| Images or diagrams don't show | Open the notebook from inside the repository, so relative paths resolve |
