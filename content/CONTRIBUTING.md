# Contributing

Thank you for helping improve the course. Learners find most of the mistakes in course material, so reports are genuinely useful.

## Reporting a problem

Open an issue on this repository's GitHub page, or tell your instructor. Include:

- **where:** the file, and the notebook cell or section;
- **what happened:** the command you ran and the full output, or the text you think is wrong;
- **what you expected;**
- your operating system, and the output of `uv --version` and `uv run python --version`.

Please **never** include API keys, `.env` contents, or anything from your employer in an issue. Check screenshots and logs for them before you post.

Useful reports include: a command that doesn't work as written, a notebook cell that fails from a fresh kernel, a broken link, a test that fails on a correct solution, an explanation that's wrong or unclear, and a diagram that doesn't match the text.

## Suggesting a change

Small fixes (typos, broken links, clearer wording) are welcome as pull requests. For anything larger, open an issue first, so we can agree on the change before you spend time on it.

Before opening a pull request:

```bash
uv sync
uv run python scripts/validate_repository.py
uv run python scripts/validate_notebooks.py
```

Both should report no failures. Notebooks must be committed **without outputs**: use "Clear All Outputs" before saving.

## What doesn't belong here

- **Your assignment solutions.** Keep your work in your own repository (and keep it private if your course instructions say so). Solutions in this repository would spoil the workbooks for everyone else.
- Real company data, personal data, or credentials of any kind. All course data is synthetic.

## Conventions

- Python 3.13, managed with `uv`; formatted and linted with Ruff.
- Diagrams are SVG files in `assets/diagrams/`, using the course colour palette. Every diagram in a lesson is followed by a **How this works** list.
- Writing is plain, direct English for experienced developers.
