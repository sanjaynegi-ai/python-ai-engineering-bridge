"""Validate the course repository: structure, links, code, configuration, diagrams and secrets.

Run from the repository root:

    uv run python scripts/validate_repository.py              # local checks
    uv run python scripts/validate_repository.py --external   # also check external links (slower)

Every check is reported as Passed, Failed, Skipped (it couldn't run here, for example
because a tool is missing) or Not executed (not requested). Skipped checks are never
counted as passed. The exit code is 1 if anything failed.

Notebook checks live in validate_notebooks.py.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT_FILES = [
    "README.md",
    "COURSE_MAP.md",
    "PREREQUISITES.md",
    "LEARNING_OUTCOMES.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    ".gitignore",
    ".python-version",
    ".env.example",
    "pyproject.toml",
    "uv.lock",
    "requirements.txt",
]
DOCS = [
    "getting-started.md",
    "setup-vscode.md",
    "setup-uv.md",
    "setup-venv.md",
    "setup-conda.md",
    "using-jupyter.md",
    "using-claude-code.md",
    "debugging-python.md",
    "api-key-security.md",
    "troubleshooting.md",
]
SESSION_FILES = [
    "README.md",
    "notebooks/01-concepts.ipynb",
    "notebooks/02-practice-quiz.ipynb",
    "workbook/assignment.md",
    "resources/references.md",
]
PROJECT_FILES = ["README.md", "pyproject.toml", "uv.lock", ".python-version"]

SKIP_DIRS = {
    ".venv",
    ".git",
    "__pycache__",
    ".ruff_cache",
    ".pytest_cache",
    "out",
    "node_modules",
}
TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".json",
    ".jsonl",
    ".ipynb",
    ".svg",
    ".yml",
    ".yaml",
}
TEXT_NAMES = {".env.example", ".gitignore", ".python-version"}
SMALL_FILE_OK = {".python-version", "__init__.py", "py.typed"}
PALETTE = {"#2563EB", "#0D9488", "#7C3AED", "#D97706", "#64748B", "#DC2626"}
SVG_NS = "{http://www.w3.org/2000/svg}"
SECRET = re.compile(
    r"sk-ant-[A-Za-z0-9_-]{8,}|sk-(?:proj-)?[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}"
    r"|ghp_[A-Za-z0-9]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
)
PLACEHOLDER = re.compile(r"TODO: write|Lorem ipsum|\bTBD\b|coming soon", re.IGNORECASE)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ALLOWED_EMAIL_DOMAINS = (
    "example.com",
    "example.org",
    "example.invalid",
    "anthropic.com",
)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/141 Safari/537.36"


class Report:
    def __init__(self) -> None:
        self.results: dict[str, list[str]] = defaultdict(list)

    def check(self, ok: bool, name: str, detail: str = "") -> None:
        self.results["passed" if ok else "failed"].append(
            f"{name}: {detail}".rstrip(": ")
        )

    def skip(self, name: str, reason: str) -> None:
        self.results["skipped"].append(f"{name}: {reason}")

    def not_executed(self, name: str, reason: str) -> None:
        self.results["not executed"].append(f"{name}: {reason}")

    def print(self, verbose: bool) -> int:
        for status in ("failed", "skipped", "not executed") + (
            ("passed",) if verbose else ()
        ):
            for line in self.results[status]:
                print(f"{status.upper():<13} {line}")
        counts = "  ".join(
            f"{status.capitalize()}: {len(self.results[status])}"
            for status in ("passed", "failed", "skipped", "not executed")
        )
        print(f"\n{counts}")
        return 1 if self.results["failed"] else 0


def files(root: Path):
    """Every file under root, skipping environments, caches and generated output."""
    for path in sorted(root.rglob("*")):
        if path.is_file() and not SKIP_DIRS.intersection(path.relative_to(root).parts):
            yield path


def is_text(path: Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name in TEXT_NAMES


def strip_code(markdown: str) -> str:
    """Remove fenced code blocks and inline code, where link-like text isn't a link."""
    markdown = re.sub(r"```.*?```", "", markdown, flags=re.DOTALL)
    return re.sub(r"`[^`\n]*`", "", markdown)


def markdown_of(path: Path) -> str:
    if path.suffix == ".ipynb":
        notebook = json.loads(path.read_text(encoding="utf-8"))
        return "\n\n".join(
            "".join(cell["source"])
            for cell in notebook["cells"]
            if cell["cell_type"] == "markdown"
        )
    return path.read_text(encoding="utf-8")


def github_slug(heading: str) -> str:
    slug = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return slug.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    text = strip_code(markdown_of(path)) if path.suffix in {".md", ".ipynb"} else ""
    found = {
        github_slug(m.group(1)) for m in re.finditer(r"^#+\s+(.*)$", text, re.MULTILINE)
    }
    found |= set(re.findall(r'<a (?:id|name)="([^"]+)"', text))
    return found


# -- checks ----------------------------------------------------------------------------


def check_structure(root: Path, report: Report) -> None:
    for name in ROOT_FILES:
        report.check((root / name).is_file(), "structure", name)
    for name in DOCS:
        report.check((root / "docs" / name).is_file(), "structure", f"docs/{name}")

    sessions = sorted(p for p in (root / "sessions").glob("session-*") if p.is_dir())
    numbers = [int(p.name.split("-")[1]) for p in sessions]
    expected = list(range(0, max(numbers) + 1)) if numbers else []
    report.check(
        numbers == expected,
        "structure",
        f"sessions are contiguous from 00 ({len(numbers)} present)",
    )
    for session in sessions:
        for name in SESSION_FILES:
            report.check(
                (session / name).is_file(), "structure", f"{session.name}/{name}"
            )

    for project in sorted(p for p in (root / "projects").glob("*") if p.is_dir()):
        report.check(
            (project / "README.md").is_file(), "structure", f"{project.name}/README.md"
        )
        for stage in ("starter", "checkpoint"):
            if (project / stage).is_dir():
                for name in PROJECT_FILES:
                    report.check(
                        (project / stage / name).is_file(),
                        "structure",
                        f"{project.name}/{stage}/{name}",
                    )


def check_placeholders(root: Path, report: Report) -> None:
    for path in files(root):
        if not is_text(path) or path.suffix == ".svg":
            continue
        relative = path.relative_to(root).as_posix()
        if path.name not in SMALL_FILE_OK and path.stat().st_size < 50:
            report.check(False, "placeholder", f"{relative} is under 50 bytes")
            continue
        if path.suffix in {".md", ".ipynb"} and PLACEHOLDER.search(markdown_of(path)):
            report.check(False, "placeholder", f"{relative} contains placeholder text")
    report.check(
        True, "placeholder", "no empty or placeholder files besides those listed"
    )


def check_links(root: Path, report: Report) -> set[str]:
    external: set[str] = set()
    cache: dict[Path, set[str]] = {}
    for path in files(root):
        if path.suffix not in {".md", ".ipynb"}:
            continue
        text = strip_code(markdown_of(path))
        targets = re.findall(r"\]\(([^)\s]+)\)", text) + re.findall(
            r'src="([^"]+)"', text
        )
        for target in targets:
            if target.startswith(("http://", "https://")):
                external.add(target)
                continue
            if target.startswith("mailto:"):
                continue
            file_part, _, anchor = target.partition("#")
            destination = (path.parent / file_part).resolve() if file_part else path
            ok = destination.exists()
            if ok and anchor and destination.suffix in {".md", ".ipynb"}:
                if destination not in cache:
                    cache[destination] = anchors(destination)
                ok = anchor in cache[destination]
            if (
                ok
                and root.resolve() not in destination.resolve().parents
                and destination != root
            ):
                ok = False  # links must stay inside the repository
            report.check(ok, "link", f"{path.relative_to(root).as_posix()} -> {target}")
    return external


def check_external(urls: set[str], report: Report) -> None:
    for url in sorted(urls):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                report.check(
                    response.status < 400, "external link", f"{response.status} {url}"
                )
        except urllib.error.HTTPError as error:
            if error.code in (
                403,
                429,
            ):  # bot protection or rate limiting, not a broken link
                report.skip(
                    "external link",
                    f"{url}: the site refused an automated check "
                    f"(HTTP {error.code}); open it in a browser",
                )
            else:
                report.check(False, "external link", f"{url} ({error})")
        except Exception as error:  # noqa: BLE001 - every failure is reported, none hidden
            report.check(False, "external link", f"{url} ({error})")


def check_python(root: Path, report: Report) -> None:
    """Compile every .py file in memory: syntax errors fail; nothing is written to disk."""
    count = 0
    for path in files(root):
        if path.suffix == ".py":
            count += 1
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
            except SyntaxError as error:
                report.check(
                    False, "python compiles", f"{path.relative_to(root)}: {error}"
                )
    report.check(True, "python compiles", f"{count} files checked")


def check_ruff(root: Path, report: Report) -> None:
    try:
        subprocess.run(
            [sys.executable, "-m", "ruff", "--version"], capture_output=True, check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        report.skip("ruff", "ruff is not installed in this environment (run `uv sync`)")
        return
    # Notebooks aren't linted: their code deliberately includes bugs. Project add-on folders
    # (projects/*/session-NN) are copied into a learner's project, so they're checked
    # with that project's starter configuration. Workbook stubs in sessions import
    # names that learners will use, so unused imports (F401) are expected there.
    add_ons = sorted(p for p in (root / "projects").glob("*/session-*") if p.is_dir())
    excludes = ["--extend-exclude", "*.ipynb"]
    for folder in add_ons:
        excludes += ["--extend-exclude", folder.relative_to(root).as_posix()]
    stub_imports = [
        "--extend-per-file-ignores",
        "sessions/*/workbook/starter/*.py:F401",
    ]
    runs = [(root, excludes + stub_imports, excludes)]
    for folder in add_ons:
        # In a learner's project, the starter and every earlier add-on share one src/
        earlier = [
            f"../{p.name}/src"
            for p in add_ons
            if p.parent == folder.parent and p < folder
        ]
        sources = ", ".join(repr(path) for path in ["src", "../starter/src", *earlier])
        # An add-on's tests may import modules the learner hasn't written yet, so name
        # the project's packages explicitly rather than relying on finding the files.
        packages = sorted(
            p.name for p in (folder.parent / "starter" / "src").iterdir() if p.is_dir()
        )
        first_party = ", ".join(repr(name) for name in packages)
        config = ["--config", str(folder.parent / "starter" / "pyproject.toml")]
        check = [
            *config,
            "--config",
            f"src = [{sources}]",
            "--config",
            f"lint.isort.known-first-party = [{first_party}]",
        ]
        runs.append((folder, check, config))
    for folder, check_args, format_args in runs:
        relative = folder.relative_to(root).as_posix() or "."
        for command, extra, name in (
            (["check", "--quiet"], check_args, "ruff check"),
            (["format", "--check"], format_args, "ruff format"),
        ):
            result = subprocess.run(
                [sys.executable, "-m", "ruff", *command, "--no-cache", *extra, "."],
                cwd=folder,
                capture_output=True,
                text=True,
                check=False,
            )
            lines = (result.stdout + result.stderr).strip().splitlines()
            summary = lines[-1] if lines else "clean"
            report.check(result.returncode == 0, name, f"{relative}: {summary}")


def check_projects(root: Path, report: Report) -> None:
    uv = shutil.which("uv")
    for pyproject in sorted(root.rglob("pyproject.toml")):
        if SKIP_DIRS.intersection(pyproject.relative_to(root).parts):
            continue
        folder = pyproject.parent
        relative = folder.relative_to(root).as_posix() or "."
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as error:
            report.check(False, "pyproject parses", f"{relative}: {error}")
            continue
        report.check(True, "pyproject parses", relative)
        project = data.get("project", {})
        report.check(
            "authors" not in project, "no personal data in pyproject", relative
        )
        report.check(
            project.get("requires-python") == ">=3.13",
            "requires-python is >=3.13",
            relative,
        )
        if (folder / ".python-version").is_file():
            version = (folder / ".python-version").read_text(encoding="utf-8").strip()
            report.check(version == "3.13", ".python-version is 3.13", relative)
        if not (folder / "uv.lock").is_file():
            report.check(False, "uv.lock present", relative)
        elif uv is None:
            report.skip("uv lock --check", f"{relative}: uv is not on PATH")
        else:
            result = subprocess.run(
                [uv, "lock", "--check"],
                cwd=folder,
                capture_output=True,
                text=True,
                check=False,
            )
            report.check(result.returncode == 0, "uv.lock is up to date", relative)

    requirements = root / "requirements.txt"
    if uv is None:
        report.skip("requirements.txt in sync", "uv is not on PATH")
    elif requirements.is_file():
        expected = subprocess.run(
            [uv, "export", *EXPORT_ARGS],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        ).stdout
        report.check(
            _requirement_lines(expected)
            == _requirement_lines(requirements.read_text("utf-8")),
            "requirements.txt in sync with uv.lock",
            "regenerate with: uv export "
            + " ".join(EXPORT_ARGS)
            + " -o requirements.txt",
        )


EXPORT_ARGS = [
    "--format",
    "requirements.txt",
    "--no-hashes",
    "--no-emit-project",
    "--quiet",
]


def _requirement_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.startswith("#")
    ]


def check_svgs(root: Path, report: Report) -> None:
    for svg in sorted((root / "assets" / "diagrams").glob("*.svg")):
        text = svg.read_text(encoding="utf-8")
        try:
            element = ET.fromstring(text)
        except ET.ParseError as error:
            report.check(False, "svg well-formed", f"{svg.name}: {error}")
            continue
        report.check(element.get("viewBox") is not None, "svg viewBox", svg.name)
        has_text = element.find(f"{SVG_NS}title") is not None
        report.check(
            has_text and element.find(f"{SVG_NS}desc") is not None,
            "svg title/desc",
            svg.name,
        )
        report.check(element.get("role") == "img", "svg role=img", svg.name)
        report.check(
            "<script" not in text
            and "<foreignObject" not in text
            and 'href="http' not in text,
            "svg has no scripts or external resources",
            svg.name,
        )
        strokes = set(re.findall(r'stroke="(#[0-9A-Fa-f]{6})"', text))
        report.check(
            strokes <= PALETTE,
            "svg strokes use the palette",
            f"{svg.name} {sorted(strokes - PALETTE) or ''}",
        )


def check_diagram_explanations(root: Path, report: Report) -> None:
    pattern = re.compile(
        r"!\[[^\]]*\]\([^)]*\.svg\)|<img [^>]*src=\"[^\"]*\.svg\"[^>]*>"
    )
    for path in files(root):
        if path.suffix not in {".md", ".ipynb"}:
            continue
        cells = (
            [
                "".join(c["source"])
                for c in json.loads(path.read_text("utf-8"))["cells"]
                if c["cell_type"] == "markdown"
            ]
            if path.suffix == ".ipynb"
            else [path.read_text(encoding="utf-8")]
        )
        for cell in cells:
            for match in pattern.finditer(cell):
                after = cell[match.end() :]
                explained = (
                    re.match(r"\s*\*\*How this works\*\*\s*\n\s*\n- ", after)
                    is not None
                )
                report.check(
                    explained,
                    "diagram explained",
                    f"{path.relative_to(root).as_posix()}: {match.group(0)[:60]}",
                )


def check_secrets(root: Path, report: Report) -> None:
    for path in files(root):
        if not is_text(path) or path.name == "uv.lock":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        relative = path.relative_to(root).as_posix()
        hits = SECRET.findall(text)
        report.check(not hits, "no secrets", f"{relative} {hits[:2] or ''}")
        emails = [
            e
            for e in EMAIL.findall(text)
            if not e.lower().endswith(ALLOWED_EMAIL_DOMAINS)
        ]
        emails = [e for e in emails if not re.search(r"\.(png|svg|jpg|py)$", e)]
        report.check(
            not emails, "no personal email addresses", f"{relative} {emails[:2] or ''}"
        )
    report.check(
        not (root / ".env").exists() or _ignored(root, ".env"),
        "no .env in the repository",
    )


def _ignored(root: Path, name: str) -> bool:
    gitignore = root / ".gitignore"
    return gitignore.is_file() and name in gitignore.read_text(encoding="utf-8").split()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument(
        "--external", action="store_true", help="also check external links"
    )
    parser.add_argument("--verbose", action="store_true", help="list passed checks too")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    report = Report()

    check_structure(root, report)
    check_placeholders(root, report)
    external = check_links(root, report)
    if args.external:
        check_external(external, report)
    else:
        report.not_executed("external links", f"{len(external)} links; use --external")
    check_python(root, report)
    check_ruff(root, report)
    check_projects(root, report)
    check_svgs(root, report)
    check_diagram_explanations(root, report)
    check_secrets(root, report)
    return report.print(args.verbose)


if __name__ == "__main__":
    sys.exit(main())
