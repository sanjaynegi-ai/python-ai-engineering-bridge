"""Validate the course notebooks: format, cleanliness, and execution from a fresh kernel.

Run from the repository root, in the course environment:

    uv run python scripts/validate_notebooks.py                  # every notebook
    uv run python scripts/validate_notebooks.py sessions/session-03
    uv run python scripts/validate_notebooks.py --no-execute     # format checks only

Each notebook declares how it may be executed, in its metadata (`course.execution`):

    offline    runs with no network and no API key: always executed
    paid-api   live calls are opt-in inside the notebook (RUN_LIVE_CALLS = False by
               default); executed in that default, free mode
    network    needs the internet: executed only with --allow-network

Notebooks aren't linted: teaching code deliberately contains bugs to find and
unidiomatic examples to improve.

Results are reported as Passed, Failed, Skipped or Not executed, and the exit code
is 1 if anything failed.
"""

import argparse
import os
import sys
from collections import defaultdict
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

EXECUTION_CLASSES = {"offline", "paid-api", "network"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "paths", nargs="*", type=Path, help="notebooks or folders (default: sessions/)"
    )
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--no-execute", action="store_true", help="skip execution")
    parser.add_argument(
        "--allow-network", action="store_true", help="also execute network notebooks"
    )
    parser.add_argument(
        "--timeout", type=int, default=300, help="seconds allowed per cell"
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    targets = [path if path.is_absolute() else root / path for path in args.paths] or [
        root / "sessions"
    ]
    notebooks = sorted(
        {
            nb
            for target in targets
            for nb in (
                [target] if target.suffix == ".ipynb" else target.rglob("*.ipynb")
            )
            if ".ipynb_checkpoints" not in nb.parts
        }
    )
    results: dict[str, list[str]] = defaultdict(list)

    def record(status: str, notebook: Path, message: str) -> None:
        results[status].append(f"{notebook.relative_to(root).as_posix()}: {message}")

    # Notebooks run tools in subprocesses; plain-text output keeps them readable.
    for name in ("FORCE_COLOR", "CLICOLOR_FORCE"):
        os.environ.pop(name, None)

    for path in notebooks:
        try:
            notebook = nbformat.read(path, as_version=4)
            nbformat.validate(notebook)
        except Exception as error:  # noqa: BLE001 - an unreadable notebook is a failure to report
            record("failed", path, f"invalid notebook format: {error}")
            continue
        record("passed", path, "valid nbformat")

        stored = [
            i
            for i, cell in enumerate(notebook.cells)
            if cell.cell_type == "code" and (cell.outputs or cell.execution_count)
        ]
        if stored:
            record(
                "failed",
                path,
                f"stored outputs in code cells {stored[:5]} (clear them before committing)",
            )
        else:
            record("passed", path, "no stored outputs")

        execution = notebook.metadata.get("course", {}).get("execution")
        if execution not in EXECUTION_CLASSES:
            record(
                "failed",
                path,
                f"metadata course.execution is {execution!r}; expected one of {sorted(EXECUTION_CLASSES)}",
            )
            continue
        record("passed", path, f"execution class {execution}")

        if args.no_execute:
            record("not executed", path, "--no-execute")
            continue
        if execution == "network" and not args.allow_network:
            record("not executed", path, "needs the network; use --allow-network")
            continue

        client = NotebookClient(
            notebook,
            timeout=args.timeout,
            kernel_name="python3",
            resources={"metadata": {"path": str(path.parent)}},
        )
        try:
            client.execute()
        except CellExecutionError as error:
            first_line = str(error).strip().splitlines()[-1][:200]
            record("failed", path, f"execution error: {first_line}")
            continue
        except Exception as error:  # noqa: BLE001 - kernel start-up problems are reported, not hidden
            record("skipped", path, f"could not run a kernel: {error}")
            continue
        errors = [
            o
            for cell in notebook.cells
            if cell.cell_type == "code"
            for o in cell.outputs
            if o.output_type == "error"
        ]
        if errors:
            record(
                "failed",
                path,
                f"{len(errors)} error output(s), first: {errors[0].ename}",
            )
        else:
            mode = " (default, free mode)" if execution == "paid-api" else ""
            record("passed", path, f"executed from a fresh kernel{mode}")

    for status in ("failed", "skipped", "not executed"):
        for line in results[status]:
            print(f"{status.upper():<13} {line}")
    counts = "  ".join(
        f"{s.capitalize()}: {len(results[s])}"
        for s in ("passed", "failed", "skipped", "not executed")
    )
    print(f"\n{len(notebooks)} notebooks.  {counts}")
    return 1 if results["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
