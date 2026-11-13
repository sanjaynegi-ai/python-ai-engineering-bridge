# uv: Setup and Command Reference

[uv](https://docs.astral.sh/uv/) is the course's tool for Python versions, project environments and dependencies. If you know npm, Maven or NuGet, think of it as all of these for Python, plus a Python installer. Session 01 explains how it works; this page is the reference.

Installation is in [`getting-started.md`](getting-started.md). The course needs **uv 0.13 or newer** (`uv --version`).

## The files uv manages

| File | What it is | Commit it? |
|---|---|---|
| `pyproject.toml` | Your project's declaration: name, Python version, dependencies, tool settings | Yes |
| `uv.lock` | The exact version of every package, direct and indirect, for every platform | Yes |
| `.python-version` | The Python version for this project, for example `3.13` | Yes |
| `.venv/` | The project's environment, created from the lockfile | **No**: it's recreated with `uv sync` |

## Commands you'll use

| Task | Command |
|---|---|
| Install a Python version | `uv python install 3.13` |
| List installed and available Pythons | `uv python list` |
| Create a project | `uv init my-project` (a package with a `src/` layout); `uv init --no-package my-script` (a simple project) |
| Pin the project's Python version | `uv python pin 3.13` |
| Add a dependency | `uv add httpx` |
| Add a development-only dependency | `uv add --dev pytest` |
| Remove a dependency | `uv remove httpx` |
| Create or update `.venv` from the lockfile | `uv sync` |
| The same, failing if the lockfile is out of date (CI) | `uv sync --locked` |
| Run a command in the project's environment | `uv run python main.py`, `uv run pytest`, `uv run incident-report` |
| Update the lockfile after editing `pyproject.toml` | `uv lock` |
| Check that the lockfile is up to date | `uv lock --check` |
| Upgrade one dependency within its constraints | `uv lock --upgrade-package httpx`, then `uv sync` |
| Show the dependency tree | `uv tree` |
| Export pinned requirements for pip | `uv export --format requirements.txt --no-hashes -o requirements.txt` |

**Always use `uv run`** (or a terminal where `.venv` is activated). Running plain `python` may pick up a different interpreter that doesn't have your packages. That's the "wrong interpreter" problem from Session 01.

## Dependency groups

Development tools such as pytest and Ruff go in a **dependency group** rather than in the project's dependencies:

```toml
[dependency-groups]
dev = ["pytest>=9.1.1", "ruff>=0.17.1"]
```

`uv add --dev pytest` adds to the `dev` group. `uv sync` installs it by default; `uv sync --no-dev` leaves it out, for example in a production image.

The course repository itself uses groups for topics (`dev`, `web` ...), all installed by default through `[tool.uv] default-groups` in its `pyproject.toml`.

## Compared with other ecosystems

| | npm | Maven / Gradle | NuGet | uv |
|---|---|---|---|---|
| Declaration | `package.json` | `pom.xml` / `build.gradle` | `.csproj` | `pyproject.toml` |
| Lockfile | `package-lock.json` | (Gradle lockfiles, optional) | `packages.lock.json` | `uv.lock` |
| Installed packages | `node_modules/` | a shared cache | a shared cache | `.venv/`, per project |
| Dev-only dependencies | `devDependencies` | `test` scope | `PrivateAssets` | a dependency group |
| Run a project command | `npm run` / `npx` | `mvn` / `gradle` tasks | `dotnet run` | `uv run` |

## Updating uv

If you installed uv with the official installer:

```bash
uv self update
```

If you used Homebrew or winget, update it with that tool instead.

## Further reading

- [uv documentation](https://docs.astral.sh/uv/), especially "Working on projects".
- [`setup-venv.md`](setup-venv.md) and [`setup-conda.md`](setup-conda.md), if you can't use uv.
