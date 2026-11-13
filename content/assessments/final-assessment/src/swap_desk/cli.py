"""Command line: `swap-desk breaches ROTA.json` lists engineers who break the rota rule."""

import argparse
import json
import sys
from pathlib import Path

from swap_desk.rota import rule_breaches


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="swap-desk", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    breaches = commands.add_parser("breaches", help="engineers on call too many weeks in a row")
    breaches.add_argument("rota", type=Path)
    breaches.add_argument("--max", type=int, default=2, help="consecutive weeks allowed")
    args = parser.parse_args(argv)

    try:
        rows = json.loads(args.rota.read_text(encoding="utf-8"))
        names = rule_breaches(rows, max_consecutive=args.max)
    except (OSError, ValueError, KeyError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    for name in names:
        print(name)
    return 1 if names else 0
