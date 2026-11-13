# Session 02 Assignment: The Morning Incident Summary

**Type:** Independent. Complete this without an AI coding assistant; Session 13 covers AI-assisted work.
**Estimated time:** 2 hours
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb) and [`03-collections-deep-dive.ipynb`](../notebooks/03-collections-deep-dive.ipynb)

---

## Business scenario

Every morning, the Orbital Logistics (fictional) on-call lead opens the overnight ticket export and works out by hand which teams are drowning, which tickets have breached their SLA, and what the recurring themes are. It takes twenty minutes, and the numbers are often wrong, because the export is messy:

- Team names arrive as `Platform`, `platform` and `" network "`.
- Statuses arrive as `open`, `Open` and `OPEN`.
- A ticket that's updated during the export appears **twice**.
- "No assignee" is sometimes `None`, sometimes `""` and sometimes `"  "`.

Your job is a small utility, `ticket_summary.py`, that cleans the export and prints the summary. You'll write it as a set of small functions that each take data and return **new** data, the style that later sessions (and Project 01) build on.

## Learning objectives

By completing this assignment you will:

- **Implement** data cleaning with string methods, and **avoid** mutating the caller's data.
- **Choose** the right collection for each step: a set for "seen" checks, dicts for grouping and counting, tuples for ranked pairs.
- **Write** comprehensions for filter-and-transform steps, and loops where a comprehension would hurt readability.
- **Apply** `is None` and truthiness deliberately, including for blank strings.
- **Sort** records by several keys, including a descending key with an alphabetical tie-break.
- **Debug** aliasing and mutation bugs by reading which check fails and why.

## Prerequisites

- Session 01 completed: `uv` installed and working.
- Both Session 02 concept notebooks worked through.
- The course repository cloned, so that you can copy the starter files from it.

No third-party packages are needed. Everything uses the standard library, plus Ruff as a development tool.

---

## Project setup

Work in your own folder **outside** the course repository, as in Session 01:

```bash
uv init --no-package --python 3.13 ticket-summary
cd ticket-summary
uv add --dev ruff
```

Copy the three starter files from the course repository into your project folder. Adjust the path to wherever you cloned the course:

```bash
# macOS / Linux / Git Bash
cp ~/python-ai-engineering-bridge/sessions/session-02/workbook/starter/*.py .

# PowerShell
Copy-Item ~\python-ai-engineering-bridge\sessions\session-02\workbook\starter\*.py .
```

You won't need the `main.py` that `uv init` created, so delete it.

| Starter file | What it is | Edit it? |
|---|---|---|
| `sample_tickets.py` | 16 synthetic ticket records, the SLA table and the closed statuses | **No** |
| `ticket_summary.py` | Function signatures and docstrings, each raising `NotImplementedError` | **Yes**, this is your work |
| `check_summary.py` | 16 acceptance checks that call your functions | **No** |

Run the checker straight away:

```bash
uv run check_summary.py
```

Every check should say `TODO`, and the last line should read `Passed: 0  Failed: 0  Not implemented: 16`. The exit code is `1` until everything passes.

> **Why not pytest?** pytest arrives in Session 04, where you'll turn checks like these into a real test suite. For now `check_summary.py` plays that role: a script that exercises your functions and reports what's wrong.

---

## Requirements

| # | Requirement |
|---|---|
| R1 | Every function in `ticket_summary.py` behaves as its docstring describes, and all 16 checks in `check_summary.py` pass. |
| R2 | **No function modifies the data it is given**, including nested lists such as `tags`. |
| R3 | Deduplication keeps the **first** occurrence of each ticket ID and preserves the original order. |
| R4 | A ticket breaches its SLA only if it is open **and** its age is **strictly greater** than the limit for its priority. |
| R5 | `team_summary` includes **every** team that appears in the input, including teams with no open tickets (whose oldest age is `None`). |
| R6 | `top_tags` orders by count, highest first, and breaks ties **alphabetically**. |
| R7 | `uv run ticket_summary.py` prints the report shown in Milestone 7. |
| R8 | `uv run ruff check .` and `uv run ruff format --check .` both pass. |

## Suggested structure

```text
ticket-summary/
├── .gitignore
├── .python-version
├── NOTES.md              ← you create this (milestones 2 and 8, and the reflection)
├── README.md
├── check_summary.py      ← provided, don't edit
├── pyproject.toml
├── sample_tickets.py     ← provided, don't edit
├── ticket_summary.py     ← your implementation
└── uv.lock
```

Keep everything in `ticket_summary.py` for this assignment. Splitting code into modules and packages is Session 04's topic.

---

## Implementation milestones

### Milestone 1: Read before you write (10 min)

1. Open `ticket_summary.py` and read every docstring. Each one is a specification.
2. Open `sample_tickets.py`. Note that `CLOSED_STATUSES` is a **set** and `SLA_HOURS` is a **dict**. Why is each the right type for how it will be used? (`03-collections-deep-dive.ipynb`, Part 1.)
3. Run `uv run ruff check .`. It reports that the imports in `ticket_summary.py` are unused. That's expected: you'll use them as you implement the functions, and the warnings will go away.

### Milestone 2: Explore the data (15 min)

Before cleaning data, find out *how* it's dirty. Start an interactive session with the data loaded:

```bash
uv run python -i sample_tickets.py
```

`-i` runs the file and then leaves you at a `>>>` prompt with `TICKETS` available. Answer these with one-line comprehensions, `set()`, `sorted()` and `collections.Counter`, not by reading the file:

1. How many records are there, and how many **distinct** ticket IDs?
2. Which ticket IDs appear more than once?
3. What are all the distinct values of `team`? Of `status`? (Wrap values in `repr()` to see the whitespace.)
4. Which records have an assignee that is "missing" in some sense?

Leave with `exit()`. In `NOTES.md`, list **at least five** data-quality problems you found, and the expression you used to find each.

### Milestone 3: `normalise_ticket` (20 min)

Implement it so that the first four checks pass.

Hints:

- Strings are immutable: `.strip()` and `.lower()` return new strings (`01-concepts.ipynb`, Part 2).
- `None` has no `.strip()` method. Handle "missing" and "blank" assignees so that both become `None`. Think about whether `or`, an `if`, or `is None` expresses that most clearly.
- Tags: lower-case them, drop duplicates and sort. A set comprehension inside `sorted()` does all three in one line.
- To return a **new** dict, either build it as a dict literal, or start from `dict(ticket)` (a shallow copy) and replace keys. Answer in `NOTES.md`: *why is a shallow copy safe here, given that `tags` is a list?*

Run the checker after each change:

```bash
uv run check_summary.py
```

### Milestone 4: `deduplicate`, `is_open` and `is_breached` (20 min)

- `deduplicate`: the "seen set" pattern from the deep-dive notebook, Part 5. Why is `set(tickets)` not an option here? (Try it and read the error.)
- `is_open`: one line. It receives tickets that are already normalised, so you don't need to lower-case again.
- `is_breached`: watch the boundary. A P2 ticket that is exactly 24 hours old has **not** breached.

### Milestone 5: `count_by` and `group_by_team` (15 min)

- `count_by` takes the **field name** as a parameter, so `count_by(tickets, "priority")` and `count_by(tickets, "status")` use the same code. `Counter` returns a `dict` subclass; the checker accepts either.
- `group_by_team`: `defaultdict(list)` is the standard group-by. Convert it back to a plain `dict` before returning it, so callers aren't surprised when a missing key silently creates an entry.

### Milestone 6: `team_summary` (25 min)

This is the hardest function. Work it out on paper for one team before you code it.

- **Every** team in the input must appear (R5), even with nothing open. Create an entry for each team first, then fill it in.
- If you create those entries with `dict.fromkeys(teams, [])`, re-read Part 7 of the deep-dive notebook before you run anything.
- `sum()` over booleans counts the `True`s.
- `max()` of an empty sequence raises `ValueError`. Look up the `default=` parameter.
- An assignee counts as unassigned only if it is `None`, because `normalise_ticket` already turned blanks into `None`. This is the payoff for cleaning first.

### Milestone 7: `top_tags`, then `main` (25 min)

- `Counter.most_common(n)` looks like the answer, but run the checker. Its tie order is "first seen", not alphabetical. Sort the counter's `items()` yourself with a tuple key: count descending, tag ascending.
- `main()` runs the whole pipeline: normalise every raw ticket, **then** deduplicate, then build the report. Tags are counted on **open** tickets only. Your output must match this:

```text
Orbital Logistics: morning incident summary
Records: 16 exported, 14 unique, 11 open

Team          Open  Breached  Unassigned  Oldest (h)
platform         3         3           1          26
database         4         2           2          80
it-support       2         1           1         200
network          2         1           1          12

SLA breaches, oldest first:
  INC-2007  P4  200h > 168h  Label printer queue stuck in warehouse 4
  INC-2004  P3  80h > 72h  Disk 91% full on db-03
  INC-2002  P2  30h > 24h  Nightly backup job failed
  INC-2006  P2  26h > 24h  Shipment tracking page is slow
  INC-2014  P2  25h > 24h  Monitoring alert storm after upgrade
  INC-2001  P1  7h > 4h  Checkout API returning 502s
  INC-2009  P1  5h > 4h  Intermittent DNS resolution failures

Top tags on open tickets: latency (3), network (3), api (2)
```

Teams are ranked by breaches (most first), then alphabetically. The column layout uses f-string alignment such as `{team:<12}` and `{count:>6}` (`01-concepts.ipynb`, Part 3). Exact spacing isn't checked, but the content and order are.

### Milestone 8: Break it on purpose (10 min)

Once all 16 checks pass, introduce each of these bugs **one at a time**, run the checker, record which checks fail, then undo the change:

1. In `normalise_ticket`, add a line at the top that changes the input: `ticket["team"] = ticket["team"].strip()`.
2. In `deduplicate`, keep the **last** occurrence instead of the first.
3. Change `>` to `>=` in `is_breached`.

For each one, write in `NOTES.md`: which checks failed, and **why that check catches that bug**. Then answer: bug 1 changes the team to the right value, so why does it matter? Who would be surprised, and when?

### Milestone 9: Quality gate (5 min)

```bash
uv run ruff format .
uv run ruff check .
uv run ruff format --check .
uv run check_summary.py
```

`ruff format` should leave the two provided files unchanged; if it reformats them, you've edited them by accident.

---

## Acceptance criteria

Your submission is complete when **every** row below behaves as described. Run the commands from the project folder.

| Command | Expected result |
|---|---|
| `uv run check_summary.py` | `Passed: 16  Failed: 0  Not implemented: 0`, exit code `0` |
| `uv run ticket_summary.py` | The report from Milestone 7, with the same numbers and order |
| `uv run ruff check .` | `All checks passed!` |
| `uv run ruff format --check .` | Every file already formatted |
| `git diff --stat sample_tickets.py check_summary.py` (after committing the starter files first) | No changes to the provided files |
| `NOTES.md` | Data-quality findings (M2), the shallow-copy answer (M3), the bug analysis (M8), and the reflection |

## Testing

The checker is your test suite for this assignment, and its messages are designed to be read:

```text
FAIL  team_summary
      result was {'platform': {'open': 3, ...}, ...}
      expected {'platform': {'open': 3, ...}, ...}
```

When a dict comparison fails, find the **first** key where actual and expected differ; usually one number is off. Then reproduce it in isolation with `uv run python -i ticket_summary.py`:

```python
>>> from check_summary import prepared_tickets
>>> tickets = prepared_tickets()
>>> team_summary(tickets, SLA_HOURS)["database"]
```

## Debugging guidance

| You see | Where to look |
|---|---|
| `AttributeError: 'NoneType' object has no attribute 'strip'` | An assignee is `None`. Handle the missing case before calling string methods on it. |
| A check says the input "was modified" | Something you called changes its argument in place: `.sort()`, `.append()` on the caller's list, or assigning to a key of the dict you were given. Work on a copy, or build new objects. |
| `TypeError: unhashable type: 'dict'` | You put whole tickets into a set (`set(tickets)`). Dicts are mutable, so they can't be set members. Track the **IDs** you've seen instead. |
| Every team shows the same numbers | Shared lists: see `dict.fromkeys` in the deep-dive notebook, Part 7. |
| `ValueError: max() iterable argument is empty` | A team with nothing open. Use `max(..., default=None)`. |
| `top_tags` returns the right counts in the wrong order | You used `most_common()`, or your sort key isn't (count descending, tag ascending). |
| `KeyError: 'P5'` or similar | An unknown priority. The sample data only uses P1–P4; check that you're reading `ticket["priority"]`, not another field. |
| `ModuleNotFoundError: No module named 'sample_tickets'` | Run the commands from the project folder, the one that contains `sample_tickets.py`. |
| `platform` shows an oldest age of `27` and `0` unassigned | You kept the **last** copy of `INC-2006`, not the first. Check how `deduplicate` decides which record wins. |

When you're stuck: **Observe** (which check, which value?), **Hypothesize** (what could produce that value?), **Inspect** (print the intermediate result in `python -i`), **Fix**, **Verify** (re-run the whole checker, not just the part you fixed).

## Extension challenges (optional)

1. **A breach matrix.** Add `breach_matrix(tickets, sla_hours)` returning a dict keyed by `(team, priority)` **tuples**, with breach counts as values. Print it as a table with teams as rows and priorities as columns.
2. **Command-line filters.** Let `uv run ticket_summary.py platform` print the report for one team only. Read the argument from `sys.argv`, and print a helpful message (exit code `2`) for an unknown team.
3. **At scale.** Generate 100,000 synthetic tickets with a comprehension and `random.choice`, and time your pipeline with `time.perf_counter()`. Then replace your seen-**set** in `deduplicate` with a seen-**list** and time it again. Record both timings in `NOTES.md`.
4. **Stricter input.** What should happen if a ticket has a priority missing from `SLA_HOURS`? Make the behaviour explicit, and explain your choice in `NOTES.md`. (Session 03 covers raising your own exceptions; Session 06 covers validating input properly.)

## Reflection

Answer briefly in `NOTES.md`:

1. Every function returns new data instead of changing its input. What does that cost, and what does it buy you? When might you accept mutation instead?
2. Which function would have looked most different in your main language (Java streams, C# LINQ, JavaScript array methods)? Was the Python version clearer or less clear, and why?
3. You normalised first and deduplicated second. What could go wrong with the opposite order, given this data?
4. Where did truthiness help you, and where did you need `is None` instead?

## Deliverables

Submit **one** of the following, as your course instructions specify:

- a link to a Git repository containing your project (push only to a repository you own; keep it private if you prefer), **or**
- a `.zip` of the project folder **without** `.venv/`.

The submission must include:

- [ ] `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`
- [ ] `ticket_summary.py` with all functions implemented
- [ ] `sample_tickets.py` and `check_summary.py`, unchanged
- [ ] `NOTES.md` with your answers to Milestones 2, 3 and 8, and the reflection
- [ ] All acceptance criteria passing
