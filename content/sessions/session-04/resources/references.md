# Session 04: References

Official documentation first. Each link says *why* it's worth your time, so you can pick what you need instead of reading everything.

## Modules, packages and imports

| Resource | Read it for |
|---|---|
| [Tutorial: Modules](https://docs.python.org/3/tutorial/modules.html) | Modules, `__name__`, packages and `__init__.py`, in one chapter |
| [The import system](https://docs.python.org/3/reference/import.html) | The precise rules: `sys.modules`, finders, packages, relative imports |
| [`__main__`: top-level code environment](https://docs.python.org/3/library/__main__.html) | `__main__.py` in packages, and the `if __name__` idiom |
| [Packaging guide: src layout versus flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) | Why the `src/` layout exists |
| [uv: Creating projects (applications)](https://docs.astral.sh/uv/concepts/projects/init/#applications) | What `uv init --package` creates |
| [uv: Entry points](https://docs.astral.sh/uv/concepts/projects/config/#entry-points) | `[project.scripts]` and command-line tools |

## Classes and dataclasses

| Resource | Read it for |
|---|---|
| [Tutorial: Classes](https://docs.python.org/3/tutorial/classes.html) | Python's class model, scopes, and "private" variables |
| [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) | Every option: `frozen`, `field`, `default_factory`, `replace`, `asdict` |
| [Built-in decorators: `property`](https://docs.python.org/3/library/functions.html#property) | How properties work |
| [Built-in decorators: `classmethod`](https://docs.python.org/3/library/functions.html#classmethod) | Alternative constructors |
| [Data model: special method names](https://docs.python.org/3/reference/datamodel.html#special-method-names) | The dunder methods (`__repr__`, `__eq__`, `__hash__` ...) |
| [`typing.Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol) | Optional: interfaces by structure, for duck typing with type checkers |

## pytest

| Resource | Read it for |
|---|---|
| [Get started](https://docs.pytest.org/en/stable/getting-started.html) | Installing, first tests, `pytest.raises` |
| [How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) | Fixtures, `conftest.py`, scopes and teardown with `yield` |
| [How to parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html) | `@pytest.mark.parametrize`, IDs and stacking |
| [Temporary directories and files](https://docs.pytest.org/en/stable/how-to/tmp_path.html) | `tmp_path` and `tmp_path_factory` |
| [Capturing output](https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html) | `capsys` |
| [Good integration practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html) | Test layout, the `src/` layout, and import modes |
| [Configuration](https://docs.pytest.org/en/stable/reference/customize.html) | `[tool.pytest]` in `pyproject.toml` |
| [Debugging with pytest](https://docs.pytest.org/en/stable/how-to/failures.html) | `--pdb`, `-x`, `--lf` and friends |

## Ruff

| Resource | Read it for |
|---|---|
| [Configuring Ruff](https://docs.astral.sh/ruff/configuration/) | `[tool.ruff]` settings in `pyproject.toml` |
| [Rules](https://docs.astral.sh/ruff/rules/) | Every rule code, with an explanation and an example |
| [The Ruff linter](https://docs.astral.sh/ruff/linter/) | Rule selection, fixes, and `noqa` comments |

## Debugging

| Resource | Read it for |
|---|---|
| [`pdb`: the Python debugger](https://docs.python.org/3/library/pdb.html) | All debugger commands |
| [`breakpoint()`](https://docs.python.org/3/library/functions.html#breakpoint) | How the built-in works, and `PYTHONBREAKPOINT` |
| [Python debugging in VS Code](https://code.visualstudio.com/docs/python/debugging) | Debug configurations, including `"module"` launch |
| [Python testing in VS Code](https://code.visualstudio.com/docs/python/testing) | The Testing view, running and debugging pytest tests |

---

<!-- skillup-branding:start -->
## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center">
  <img src="../../../assets/diagrams/SkillUpWithSanjay.png" alt="#SkillUpWithSanjay logo" width="60">
</p>

<p align="center">
  <strong>#SkillUpWithSanjay</strong><br>
  <a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>
  &nbsp;&middot;&nbsp;
  <a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
</p>
<!-- skillup-branding:end -->
