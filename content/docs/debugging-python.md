# Debugging Python

Debugging is a skill the course practises deliberately, with broken examples in every phase. This page is the reference. The approach is always the same:

**Observe → Hypothesize → Inspect → Fix → Verify**

1. **Observe:** read the whole error. Reproduce it reliably.
2. **Hypothesize:** write down what you think is wrong, *before* changing anything.
3. **Inspect:** check the hypothesis with evidence: print, log, debugger, a smaller test.
4. **Fix** the cause, not the symptom.
5. **Verify:** run the failing case again, then the whole test suite.

## Reading a traceback

Python prints the **most recent call last**, so read from the bottom up:

```text
Traceback (most recent call last):
  File ".../cli.py", line 42, in main
    report = build_report(tickets)
  File ".../report.py", line 18, in build_report
    hours = sla_hours[ticket.priority]
            ~~~~~~~~~^^^^^^^^^^^^^^^^^
KeyError: 'P5'
```

- **The last line** is the exception type and message: a `KeyError` for the key `'P5'`.
- **The frame above it** is where it happened: `report.py`, line 18. The `^` markers point at the failing expression.
- **Frames further up** show how the program got there. Look for the first frame in **your** code; frames inside libraries are rarely where the bug is.
- `During handling of the above exception, another exception occurred` and `The above exception was the direct cause of the following exception` mean two exceptions are chained. The first is usually the real cause.

## Tools

| Tool | When |
|---|---|
| `print(f"{value=}")` | A quick look. `=` prints the expression and its value. Remove it afterwards |
| `logging` | Information you want to keep, with levels, in services (from Session 07) |
| `breakpoint()` | Stop at a line, and inspect in the terminal |
| The VS Code debugger | Stop at a breakpoint, step through, and inspect variables visually ([`setup-vscode.md`](setup-vscode.md#debugging)) |
| `uv run pytest --pdb` | Open the debugger at the point where a test fails |
| `uv run pytest -x -vv` | Stop at the first failure, and show assertion details in full |
| `uv run pytest -k summary` | Run only tests whose names contain `summary` |
| `uv run pytest --lf` | Run only the tests that failed last time |

## The debugger in the terminal

`breakpoint()` stops the program and opens `pdb`. The commands you'll use:

| Command | Does |
|---|---|
| `p expression` | Print a value |
| `pp expression` | Pretty-print a value |
| `l` / `ll` | Show the code around the current line / the whole function |
| `n` | Run the next line |
| `s` | Step into a function call |
| `c` | Continue to the next breakpoint |
| `u` / `d` | Move up / down the call stack |
| `q` | Quit |

Remove `breakpoint()` calls before committing.

## Common errors

| Error | Usual cause |
|---|---|
| `ModuleNotFoundError: No module named 'x'` | The wrong interpreter: use `uv run`, or select `.venv` in your editor. Or the package isn't a dependency yet: `uv add x` |
| `ImportError: cannot import name 'y' from 'x'` | A typo; a circular import; or a local file with a standard-library name, such as `json.py`, shadowing the real module (Session 04's lab) |
| `AttributeError: 'NoneType' object has no attribute ...` | A function returned `None`: a missing `return`, a `.get()` that found nothing, or an LLM refusal (Session 09) |
| `TypeError: ... missing 1 required positional argument` | A call with too few arguments, or a method called on the class instead of an instance |
| `KeyError` | A missing dictionary key: check the data, or use `.get()` deliberately |
| `UnicodeDecodeError` / `UnicodeEncodeError` | A file opened without `encoding="utf-8"`, or printing special characters to an old Windows console ([`troubleshooting.md`](troubleshooting.md)) |
| `RuntimeWarning: coroutine '...' was never awaited` | A missing `await` (Session 08) |
| `pydantic.ValidationError` | Data that breaks a model's rules: read each listed field and message (Session 06) |

## When you ask for help

Include the command you ran, the **full** traceback (as text, not a screenshot), what you expected, and what you've already tried. Writing that down often reveals the answer.
