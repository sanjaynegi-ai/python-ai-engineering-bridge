"""Task 1: the project runs. Do not edit."""

import importlib
import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]


def pyproject() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_pytest_and_ruff_are_development_dependencies():
    dev = pyproject().get("dependency-groups", {}).get("dev", [])
    assert any(requirement.startswith("pytest") for requirement in dev)
    assert any(requirement.startswith("ruff") for requirement in dev)
    assert not any(r.startswith("pytest") for r in pyproject()["project"]["dependencies"])


def test_the_lockfile_includes_pytest():
    assert 'name = "pytest"' in (ROOT / "uv.lock").read_text(encoding="utf-8")


def test_the_swap_desk_command_points_at_a_real_function():
    target = pyproject()["project"]["scripts"]["swap-desk"]
    module_name, _, function_name = target.partition(":")
    function = getattr(importlib.import_module(module_name), function_name)
    assert callable(function)
