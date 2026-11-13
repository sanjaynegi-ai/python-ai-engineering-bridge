# Session 03: Functions, Exceptions, Files and JSON

**Phase 1: Python for Experienced Developers**

## Session overview

So far your data has lived inside your program. From now on it arrives from outside (files, other teams' exports, APIs and LLMs), and it is often missing, malformed or not quite what was promised.

This session covers the tools for writing code that survives that: functions designed for readable call sites, exceptions raised and handled deliberately, safe file handling with `pathlib` and `with`, and JSON parsed, validated and written back out. You'll turn the Session 02 summary into a nightly job that reports bad input instead of crashing on it.

## Why this matters

Production failures in data and AI code are rarely clever algorithmic bugs. They're a job that dies on one truncated file, a `KeyError` three functions away from the bad record that caused it, a report that silently includes yesterday's data, or text that turns into `ZÃ¼rich` on a Windows server.

Every later session depends on getting this right. HTTP clients (Session 05) translate network failures into exceptions. Pydantic (Session 06) automates the validation you'll write by hand today. LLM integrations (Session 09) must treat model output as untrusted JSON. The habits you form here (validate at the edge, chain exceptions, handle errors where you can act on them) carry through the rest of the course.

## Prerequisites

**Knowledge:** Sessions 01 and 02 completed. In particular, you can explain names, objects and mutability (Session 02, Part 1).

**Before the session:**

1. Finish the Session 02 workbook. This session's assignment imports your `ticket_summary.py` functions, so they must pass all 16 checks.
2. In the course repository, run `uv sync`, and check that `notebooks/01-concepts.ipynb` opens on the course kernel.

No new packages are needed. Everything uses the standard library.

## Learning objectives

By the end of this session you will be able to:

1. **Design** functions with positional, keyword-only and default arguments, and **avoid** the mutable-default trap by explaining when defaults are evaluated.
2. **Explain** Python's LEGB scope rules, and **fix** an `UnboundLocalError` without resorting to `global`.
3. **Annotate** functions with type hints, and **explain** why the interpreter doesn't enforce them.
4. **Raise**, **catch** and **chain** exceptions, define your own exception types, and **decide** where each failure should be handled.
5. **Read** a chained, multi-frame traceback and **locate** the first frame in your own code.
6. **Use** `pathlib` and context managers for file I/O, always with an explicit encoding, and **explain** what `with` guarantees.
7. **Parse**, **validate by hand** and **serialise** JSON, handling malformed files and invalid records without stopping the whole job.


## Concepts covered

| Concept | Depth |
|---|---|
| Functions, return values, docstrings, functions as objects | Independent implementation |
| Positional, keyword and keyword-only arguments; defaults; the mutable-default trap | Independent implementation |
| `*args`, `**kwargs`, positional-only parameters | Awareness |
| Scope (LEGB), `UnboundLocalError`, avoiding `global` | Independent implementation |
| Type hints: syntax, `X \| None`, generics; not enforced at run time | Independent implementation |
| Type checkers (mypy, pyright) | Awareness |
| `try`/`except`/`else`/`finally`, built-in exception types, EAFP versus LBYL | Independent implementation |
| Custom exception classes, `raise ... from`, reading tracebacks | Independent implementation |
| `pathlib`, `open()`, `with` and context managers, text encodings | Independent implementation |
| `json` loads/dumps/load/dump, type mapping, `JSONDecodeError` | Independent implementation |
| Hand validation of external records | Independent implementation |
| Exit codes and stderr for command-line tools | Independent implementation |



## Guided exercises

Work through [`notebooks/01-concepts.ipynb`](notebooks/01-concepts.ipynb) during and after the session:

- **The mutable default trap:** Observe → Hypothesize → Inspect → Fix → Verify on Wednesday's bug.
- **`try`/`except`/`else`/`finally`:** predict the order of execution.
- **A chained traceback:** read one line by line.
- **Encodings:** see mojibake appear, and understand why it's silent.
- **JSON round trips:** predict what survives, and what changes type.
- **Hand validation:** improve a validator to reject booleans and negative ages.
- **Debugging lab, the 02:00 crash:** make a batch job survive one bad file.

Then test yourself with [`notebooks/02-practice-quiz.ipynb`](notebooks/02-practice-quiz.ipynb) (10 questions).

## Independent assignment

[**Workbook: the nightly incident report**](workbook/assignment.md) (*Independent*: no AI coding assistant)

Build `incident_report.py`, a configurable job that reads a folder of synthetic ticket exports, rejects bad files and invalid records with clear reasons, writes a JSON report using your Session 02 functions, and returns exit codes a scheduler can act on. A checker script with 22 checks tells you which requirements pass.

## Expected deliverables

- A uv project with `incident_report.py` fully implemented, your Session 02 `ticket_summary.py` and `sample_tickets.py`, and the unchanged starter files.
- `uv run check_report.py` reporting 22 of 22 checks passed.
- `uv run incident_report.py` writing `out/report.json` and exiting with code `1` for the sample data.
- `NOTES.md` with your milestone answers, an annotated traceback and your reflection.

## Common mistakes

| Mistake | Instead |
|---|---|
| A mutable default argument (`items=[]`) | Default to `None`, create the object inside |
| Many positional options | Keyword-only parameters after `*` |
| `global` to update a counter | Pass values in, return results |
| Treating type hints as validation | Validate external data at run time |
| `except:` or `except Exception: pass` | Catch specific exceptions; handle or re-raise |
| Raising inside `except` without `from` | `raise NewError(...) from error` |
| One bad input stopping a whole batch | Handle per-item errors in the loop that owns the batch |
| `open(path)` without `with` or `encoding` | `with open(path, encoding="utf-8") as file:` |
| Assuming parsed JSON has the right shape | Check the shape, then validate every record |
| `isinstance(value, int)` for JSON numbers | Reject `bool` first |
| Tracebacks shown to users for expected failures | A one-line message on stderr and a non-zero exit code |

## Reading resources

Curated official documentation for this session: [`resources/references.md`](resources/references.md).

## Reflection questions

1. Java has checked exceptions; Python doesn't. After this session, which do you prefer, and what discipline does Python's approach demand from a team?
2. Where is the line between "validate and reject" and "raise an exception"? Give an example of each from your own work.
3. How would you explain the mutable-default trap to a colleague using only the names-and-objects model from Session 02?
4. Your job exits with code `1` when records are rejected. Who or what should react to that, and how?

## Interview questions

Practise answering these out loud and support each answer with clear engineering reasoning:

1. What's wrong with `def add(item, items=[])`? Why does Python behave this way?
2. Explain keyword-only arguments. When would you use them?
3. What does `raise X from Y` do, and why does it matter when debugging?
4. How do you read a Python traceback? Where do you start?
5. What does a `with` statement guarantee? Give two examples of context managers besides files.
6. Are Python type hints enforced? Then why use them?
7. You're loading 10,000 JSON records from a partner, and some are invalid. How do you design the loading code?

## Next-session preparation

**Session 04: Modules, Packages, Classes and Testing** turns your growing script into a properly structured package: modules and imports, a `src/` layout, dataclasses for ticket records, pytest tests replacing the checker scripts, Ruff configuration, and debugging with breakpoints. It completes **Project 01**.

Before the session:

- Finish the Session 03 workbook. Session 04 starts by splitting your `incident_report.py` and `ticket_summary.py` into a package, so you'll work on your own code.
- Notice which functions in your workbook are easy to test, and which are hard. That observation is the starting point for Session 04's testing discussion.

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
