# Troubleshooting

Problems people hit when setting up and running the course, with fixes. For errors in your own code, see [`debugging-python.md`](debugging-python.md).

If nothing here helps, ask your instructor, with the exact command, the **full** output as text, your operating system, and the output of `uv --version`.

## Installation

| Problem | Fix |
|---|---|
| `uv: command not found` (or "not recognized") right after installing | Open a **new** terminal: the installer updated `PATH`, but existing terminals don't see it. In VS Code, restart VS Code, so its integrated terminals pick up the change |
| `uv` still not found in a new terminal | The installer printed the folder it installed to. Add that folder to `PATH`, or reinstall with `brew` (macOS) or `winget` (Windows) |
| PowerShell won't run the install script | Run exactly the command in [`getting-started.md`](getting-started.md), which includes `-ExecutionPolicy ByPass`. If your company blocks it, ask IT, or use `winget install --id=astral-sh.uv -e` |
| `uv python install` fails behind a corporate proxy | Set `HTTPS_PROXY` (for example `HTTPS_PROXY=http://proxy.example.com:8080`) in the terminal before running it |
| SSL or certificate errors (`invalid peer certificate`, `UnknownIssuer`) | A company proxy inspects HTTPS. Tell uv to trust your operating system's certificates: add `--system-certs` to the command, or set `UV_SYSTEM_CERTS=1` |
| `uv sync` is very slow on Windows | Antivirus software scanning `.venv`. Ask IT to exclude your projects folder, or be patient the first time; later syncs reuse uv's cache |

## Environments and interpreters

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` when you run a script, but `uv run` works | You ran plain `python`, which isn't the project's environment. Use `uv run`, or activate `.venv` |
| `ModuleNotFoundError` in VS Code or a notebook | The wrong interpreter or kernel: select the folder's `.venv` ([`setup-vscode.md`](setup-vscode.md)) |
| `No module named ...` after `git pull` | A new session needs new packages: run `uv sync` in the course repository |
| `error: The lockfile at uv.lock needs to be updated, but --locked was provided` | `pyproject.toml` changed without `uv lock`. Run `uv lock`, then commit both files |
| Python 3.12 or older reported, or `requires-python` errors | Run `uv python install 3.13`. Check the project has `.python-version` containing `3.13` |
| Strange errors after moving or renaming a project folder | `.venv` contains absolute paths. Delete `.venv`, then run `uv sync` |

## Windows specifics

| Problem | Fix |
|---|---|
| `UnicodeEncodeError: 'charmap' codec can't encode character` | Python is printing characters the console encoding can't show. Use Windows Terminal (the default terminal on Windows 11), or set `PYTHONIOENCODING=utf-8`. In your own code, always open files with `encoding="utf-8"` |
| `fastapi dev` crashes with a `UnicodeEncodeError` | The same problem, caused by emoji in its banner: see above, or start the server with `uv run uvicorn package.module:app --reload` (Session 07) |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | Only when activating environments by hand: run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once. With `uv run` you don't need to activate |
| Paths too long when installing packages | Keep projects in a short path such as `C:\skillup`, or enable long paths in Windows (needs administrator rights) |
| Git shows every line of a file as changed | Line endings. Run `git config --global core.autocrlf true` on Windows |

## Running services

| Problem | Fix |
|---|---|
| `address already in use` / `[Errno 10048]` | Another server is still running on that port. Stop it (`Ctrl+C` in its terminal), or use another port, such as `--port 8001` |
| A server you started doesn't stop | Close its terminal, or end the `python` process in Task Manager (Windows) or with `kill` (macOS/Linux) |
| `Connection refused` to `127.0.0.1` | The server isn't running, or it's on a different port. Start it in its own terminal first |

## Notebooks

See [`using-jupyter.md`](using-jupyter.md#common-problems).

## LLM providers (from Session 09)

| Problem | Fix |
|---|---|
| `OPENAI_API_KEY is not set` | Add it to `.env` in the folder you run from, then restart the notebook kernel or the program |
| `401` or "Incorrect API key" | The key is wrong, revoked, or has a stray space or quote. Copy it again from the provider's dashboard |
| `404` or "model not found" | `LLM_MODEL` is misspelt, or your account can't use that model |
| `429` immediately, every time | Rate limits, or no credit left on the account: check the provider's dashboard |
