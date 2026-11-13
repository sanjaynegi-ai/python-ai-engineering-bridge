# Session 01: Python Runtime and Professional Setup

**Phase 1: Python for Experienced Developers**

## Session overview

You already know how to write software. This session makes sure Python's *tooling* never gets in your way. You'll learn what really happens when Python runs your code, why Python projects need isolated environments, and how to create, run and reproduce a professional Python project with **uv**.

By the end you will have a working, version-controlled project that any teammate can clone and run with a single command. That's the setup every later session builds on.

## Why this matters

Most of the time experienced developers lose in their first weeks with Python isn't spent on the language. It goes on environment problems: `ModuleNotFoundError` for a package you just installed, code that works on one laptop and not another, or an upgrade for one project that breaks another. These problems come from one Python-specific default: **packages install globally unless you opt into isolation.**

Understanding the runtime and environment model now saves you hours in every later session, from FastAPI services to RAG applications. It is also exactly what you'll need to explain when you debug someone else's broken setup in an AI engineering team.

## Prerequisites

**Knowledge:** professional experience in at least one language (Java, C#, JavaScript/TypeScript or similar), and comfort with a terminal and Git. No Python knowledge is assumed.

Before you begin, install and check the following so that you can focus on the Python work rather than environment setup.

1. **uv** (0.13 or newer), using the official installer:

   ```bash
   # macOS / Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   ```powershell
   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   Both commands download and run an install script from astral.sh. If you prefer to read a script before running it, open the URL in a browser first. Alternatives: `brew install uv` on macOS, or `winget install --id=astral-sh.uv -e` on Windows. See the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

   Open a **new** terminal afterwards, then check:

   ```bash
   uv --version
   ```

2. **Python 3.13**, installed through uv:

   ```bash
   uv python install 3.13
   ```

3. **Git** (`git --version`), and **VS Code** with the **Python** and **Jupyter** extensions from Microsoft.

4. **The course repository**, cloned, with its notebook environment created. From the repository root:

   ```bash
   uv sync
   ```

   This creates the `.venv` that the course notebooks use as their kernel.

5. **LLM provider access.** This is optional today, and needed from Session 09. The course default is **OpenAI** with the model `gpt-5.6-terra`. Anthropic (example model `claude-haiku-5-5`; the more capable `claude-opus-5-5` costs about 40× as much), OpenRouter, or a free local model through **Ollama** (`llama3.2`) work too. Part 8 of the concepts notebook walks you through creating a key, setting a spending limit, and configuring `.env`. Doing it now gives you time to sort out billing or company approvals.

6. **Embeddings.** These are needed from Session 11. The default is OpenAI's `text-embedding-3-small`, which uses the same OpenAI key. For a free, local alternative, Part 9 shows **fastembed** (`BAAI/bge-small-en-v1.5`). It is already in the course environment and downloads a 67 MB model on first use.

You do **not** need to install Python from python.org, or use `pip`, for this course.

## Learning objectives

By the end of this session you will be able to:

1. **Explain** what happens between running `python main.py` and seeing output, including which errors are caught before execution and which only appear at run time.
2. **Explain** why virtual environments exist, and **inspect** which interpreter and environment a piece of code is actually running in.
3. **Create** a uv project pinned to a specific Python version, and **add** runtime and development dependencies.
4. **Describe** the role of `pyproject.toml`, `uv.lock`, `.python-version` and `.venv/`, and decide which belong in version control.
5. **Reproduce** an environment exactly from a lockfile, and **detect** lockfile drift with `uv lock --check` and `uv sync --locked`.
6. **Debug** a `ModuleNotFoundError` caused by running the wrong interpreter, using the Observe → Hypothesize → Inspect → Fix → Verify workflow.
7. **Configure** an LLM provider (OpenAI by default, or Anthropic, OpenRouter or Ollama) through environment variables, and **explain** why API keys and model IDs belong in configuration rather than code.
8. **Generate** text embeddings with OpenAI or locally with fastembed, **rank** documents by cosine similarity, and **explain** why vectors from different models must never be mixed.


## Concepts covered

| Concept | Depth |
|---|---|
| Python execution model: bytecode, interpreter, `__pycache__`, compile-time versus run-time errors | Awareness |
| Import resolution and `sys.path` | Awareness |
| Python versions and why they matter | Awareness |
| Virtual environments: what they are, and how to detect one | Independent implementation |
| uv: `python install`, `init`, `add`, `add --dev`, `remove`, `lock`, `sync`, `run`, `tree` | Independent implementation |
| `pyproject.toml`, `uv.lock`, version specifiers | Independent implementation |
| Running scripts, modules (`-m`) and notebooks; `if __name__ == "__main__"` | Independent implementation |
| Selecting interpreters and kernels in VS Code and Jupyter | Independent implementation |
| LLM provider configuration: `.env`, API keys, OpenAI-compatible `base_url`, provider-specific model IDs, model tiers and cost | Awareness (implemented in Session 09) |
| Embeddings: OpenAI `text-embedding-3-small`, local fastembed, cosine similarity | Working knowledge (used from Session 11) |



## Guided exercises

Work through these in [`notebooks/01-concepts.ipynb`](notebooks/01-concepts.ipynb) during and after the session:

- **Which Python am I running?** Check the interpreter, version and environment from inside a running process.
- **Compile-time versus run-time errors:** predict which mistakes Python catches before running, and which wait until run time.
- **The bytecode cache:** watch `__pycache__` being created, and see a module's top-level code run only once.
- **Inside a virtual environment:** inspect `sys.prefix`, `pyvenv.cfg` and `site-packages`.
- **The lockfile is the truth:** compare locked and installed versions in the course environment.
- **Try it in your terminal:** create a scratch uv project and predict each command's effect.
- **Debugging lab:** diagnose `ModuleNotFoundError` with `importlib.util.find_spec`.
- **Preparing your LLM provider (self-study):** configure OpenAI, Anthropic, OpenRouter or Ollama through `.env`, and see one client factory serve all four. Nothing is sent unless you opt in.
- **Embeddings (self-study):** rank runbook snippets by meaning with OpenAI embeddings or a free local fastembed model, and keep the reusable `embed_texts()` helper for later sessions.

Then test yourself with [`notebooks/02-practice-quiz.ipynb`](notebooks/02-practice-quiz.ipynb).

## Independent assignment

[**Workbook: a reproducible `ops-toolkit` project**](workbook/assignment.md) (*Independent*: no AI coding assistant)

Build an environment-check command for the fictional Orbital Logistics platform team. It reports the interpreter, virtual environment and declared dependencies, exits with a meaningful status code, and fails with a clear message (not a traceback) when run with the wrong interpreter. Then prove that the project rebuilds exactly from its lockfile.

## Expected deliverables

- A Git repository (or a `.zip` without `.venv/`) containing `pyproject.toml`, `uv.lock`, `.python-version`, `main.py`, `README.md`, `.gitignore` and `NOTES.md`.
- All acceptance criteria in the workbook passing.
- `NOTES.md` with your milestone answers, the traceback you analysed, and your reflection.

## Common mistakes

| Mistake | Instead |
|---|---|
| Installing packages with a bare `pip install` | `uv add <package>` inside the project |
| Running `python main.py` from an unconfigured terminal | `uv run main.py` |
| Committing `.venv/` | Commit `uv.lock`; anyone rebuilds `.venv` with `uv sync` |
| Not committing `uv.lock` | Always commit it, because it's what makes builds reproducible |
| Editing `uv.lock` by hand | Change dependencies with `uv add` / `uv remove`; uv rewrites the lock |
| Notebook or VS Code using a different interpreter than the terminal | Select the project's `.venv` as the kernel or interpreter |
| Treating type hints as runtime checks | They aren't; validate external data explicitly (Session 06) |
| Assuming code works because it ran once | Errors in branches that never ran stay hidden; test each path |
| Pasting an API key into a notebook or source file | Put it in `.env` (git-ignored); revoke any key that was ever committed |
| Comparing embeddings made by different models | Store the model ID with the vectors; re-embed everything when the model changes |
| Using one provider's model ID with another provider | IDs differ: `claude-haiku-5-5` at Anthropic is `anthropic/claude-haiku-5.5` at OpenRouter |

## Reading resources

Curated official documentation for this session: [`resources/references.md`](resources/references.md).

## Reflection questions

1. Python catches only syntax errors before running. What practices would you put in place on a team to make up for the missing compile-time checks?
2. Why do you think Python's packaging defaults ended up global, when npm's are per project? What does uv change, and what doesn't it change?
3. When would committing `uv.lock` be the *wrong* choice? (Hint: think about libraries other people install, as opposed to applications.)
4. In your current ecosystem, what is the equivalent of `uv sync --locked` in CI, and do your pipelines use it?

## Interview questions

Practise answering these out loud and support each answer with clear engineering reasoning:

1. "Is Python compiled or interpreted?" Give an answer more precise than either word alone.
2. What is a virtual environment, physically? What does "activating" one actually do?
3. A colleague's import fails right after they installed the package. Walk me through how you would debug it.
4. What is the difference between `pyproject.toml` and `uv.lock`? Which would you edit, and which would you commit?
5. What does `if __name__ == "__main__":` do, and why does it matter for testing?
6. How would you make sure CI and production run exactly the dependency versions you tested with?
7. Your application calls OpenAI today, and the team wants to evaluate a local model through Ollama. What should have to change in the code, and what in configuration?

## Next-session preparation

**Session 02: Python Language Essentials** covers variables and object references, mutability, Python's core collections (list, tuple, dict, set), comprehensions, slicing and truthiness.

Before the session:

- Finish the Session 01 workbook. You'll use the same uv workflow for every exercise from now on.
- Make sure `uv sync` still works in the course repository, so that your notebook kernel is ready.
- Think about one data-transformation task you've written recently in your main language (grouping, filtering, aggregating records). We'll rewrite tasks like that in idiomatic Python.

---

<!-- skillup-branding:start -->
## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center">
  <img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="#SkillUpWithSanjay logo" width="60">
</p>

<p align="center">
  <strong>#SkillUpWithSanjay</strong><br>
  <a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>
  &nbsp;&middot;&nbsp;
  <a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
</p>
<!-- skillup-branding:end -->
