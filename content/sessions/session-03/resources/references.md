# Session 03: References

Official documentation first. Each link says *why* it's worth your time, so you can pick what you need instead of reading everything.

## Functions and scope

| Resource | Read it for |
|---|---|
| [Tutorial: Defining functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions) | Return values, docstrings and the basics |
| [Tutorial: More on defining functions](https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions) | Defaults (including the mutable-default warning), keyword arguments, `*` and `/` |
| [Programming FAQ: why are default values shared between objects?](https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects) | The official explanation of the mutable-default trap |
| [Programming FAQ: why am I getting an UnboundLocalError?](https://docs.python.org/3/faq/programming.html#why-am-i-getting-an-unboundlocalerror-when-the-variable-has-a-value) | Scope rules, with the exact example from this session |
| [Python scopes and namespaces](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces) | LEGB in more depth |
| [PEP 3102: Keyword-only arguments](https://peps.python.org/pep-3102/) | Why the bare `*` exists |

## Type hints

| Resource | Read it for |
|---|---|
| [`typing` module](https://docs.python.org/3/library/typing.html) | The full reference; skim the introduction and the section on unions |
| [Type hints cheat sheet (mypy)](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) | The most practical one-page summary of hint syntax |
| [PEP 604: `X \| Y` union syntax](https://peps.python.org/pep-0604/) | Why `int \| None` replaced `Optional[int]` |

## Exceptions

| Resource | Read it for |
|---|---|
| [Tutorial: Errors and exceptions](https://docs.python.org/3/tutorial/errors.html) | `try`/`except`/`else`/`finally`, raising, chaining and user-defined exceptions |
| [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) | The class hierarchy, and what each built-in exception means |
| [Exception context and chaining](https://docs.python.org/3/library/exceptions.html#exception-context) | `__cause__`, `__context__`, and how `from` changes the traceback |
| [`traceback` module](https://docs.python.org/3/library/traceback.html) | Printing and formatting tracebacks yourself |
| [Glossary: EAFP](https://docs.python.org/3/glossary.html#term-EAFP) | The "easier to ask forgiveness" style, in two sentences |

## Files

| Resource | Read it for |
|---|---|
| [`pathlib`](https://docs.python.org/3/library/pathlib.html) | Every `Path` method; the correspondence table to `os.path` at the end is useful |
| [Tutorial: Reading and writing files](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files) | `open()` modes, `with`, and file methods |
| [`open()`](https://docs.python.org/3/library/functions.html#open) | The `encoding`, `newline` and `errors` parameters in detail |
| [The `with` statement](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement) | Exactly what `with` guarantees |
| [PEP 686: Make UTF-8 mode default](https://peps.python.org/pep-0686/) | Why the default encoding differs by platform before Python 3.15 |
| [`tempfile`](https://docs.python.org/3/library/tempfile.html) | Temporary files and folders, used in the notebook and the checker |

## JSON and dates

| Resource | Read it for |
|---|---|
| [`json`](https://docs.python.org/3/library/json.html) | `load`/`dump`, `indent`, `ensure_ascii`, the conversion table and `JSONDecodeError` |
| [RFC 8259: The JSON format](https://www.rfc-editor.org/rfc/rfc8259) | The standard itself, short and readable; section 8.1 requires UTF-8 |
| [`datetime.isoformat()`](https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat) | Writing timestamps in the standard ISO 8601 format |

## Command-line programs

| Resource | Read it for |
|---|---|
| [`sys.argv`, `sys.stderr` and `sys.exit`](https://docs.python.org/3/library/sys.html#sys.argv) | Arguments, error output and exit codes |
| [`argparse` tutorial](https://docs.python.org/3/howto/argparse.html) | For the workbook's extension challenge |

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
