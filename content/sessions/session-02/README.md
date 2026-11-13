# Session 02: Python Language Essentials

**Phase 1: Python for Experienced Developers** · Weekend 1 · 2-hour live session

## 1. Session overview

You already know variables, conditions, loops and collections. This session is about how **Python** expresses them: where your instincts from Java, C# or TypeScript carry over, and where they quietly mislead you.

We start with the mental model behind most surprises in Python code: variables are **names attached to objects**, and some objects can change while others can't. Then we cover the everyday toolkit (strings, numbers, truthiness, loops, comprehensions and slicing) and spend the second half on Python's four built-in collections. You'll finish by transforming a messy export of business records into a clean summary, the kind of code every later session depends on.

## 2. Why this matters

Almost everything you'll build in this course moves data around: JSON from files and APIs, validated models, LLM outputs, document chunks. Bugs in that code are rarely syntax errors. They're a function that changes data it was handed, a "copy" that shares a nested list, a valid `0` treated as missing, or a lookup that scans a list 100,000 times.

These bugs come from Python rules that *look* familiar. Learning them precisely now means you can read other people's Python with confidence, and write data-transformation code that is correct the first time. It's also what interviewers probe when they ask about mutability, `is` versus `==`, or choosing between a list and a set.

## 3. Prerequisites

**Knowledge:** Session 01 completed. You can create a uv project, run code with `uv run`, and open the course notebooks on the course `.venv` kernel.

**Before the session:**

1. In the course repository, run `uv sync` so your notebook kernel is up to date.
2. Open `notebooks/01-concepts.ipynb` and check that the first code cell runs.
3. Think of one data-transformation task you've written recently in your main language (grouping, filtering, counting records). We'll compare it with idiomatic Python.

No new tools or packages are needed. Everything in this session uses the standard library.

## 4. Learning objectives

By the end of this session you will be able to:

1. **Predict** the behaviour of names bound to mutable and immutable objects, including aliasing through assignment and function arguments, and **choose** between a shallow and a deep copy.
2. **Explain** why only hashable objects can be dict keys or set members, and **use** tuples as composite keys.
3. **Apply** truthiness, `is None` and `==` versus `is` correctly, and **identify** cases where truthiness gives the wrong answer.
4. **Write** loops with `enumerate` and `zip`, comprehensions for filtering and transforming, and slices for taking, skipping and reversing.
5. **Choose** between list, tuple, dict and set for a given access pattern, and **justify** the choice in terms of lookups, uniqueness and mutability.
6. **Implement** a multi-step transformation over nested business records (normalise, deduplicate, filter, group, aggregate, rank) without mutating the input.
7. **Debug** aliasing and mutation bugs using Observe → Hypothesize → Inspect → Fix → Verify.

## 5. Estimated time

| Activity | Time |
|---|---:|
| Live session | 2 hours |
| Concepts notebook (revision on your own) | 50 minutes |
| Collections deep-dive notebook (revision on your own) | 50 minutes |
| Practice quiz | 35 minutes |
| Workbook assignment | 2 hours |

## 6. Concepts covered

| Concept | Depth |
|---|---|
| Names and objects, identity (`id`, `is`), aliasing, argument passing | Independent implementation |
| Mutable and immutable types; shallow and deep copies; hashability | Independent implementation |
| Dynamic and strong typing | Independent implementation |
| Numbers (`/`, `//`, `%`, floats, `round`), strings and f-strings, booleans, `None` | Independent implementation |
| Truthiness, `is None`, `==` versus `is`, chained comparisons | Independent implementation |
| Conditions, conditional expressions, `for` over items, `enumerate`, `zip(strict=True)`, `while` | Independent implementation |
| List, set and dict comprehensions; generator expressions with `sum`, `any`, `max` | Independent implementation |
| Slicing | Independent implementation |
| `list`, `tuple`, `dict`, `set`: operations, performance characteristics, selection | Independent implementation |
| Sorting with `key=`, `sorted()` versus `.sort()` | Independent implementation |
| Unpacking, including `*rest` | Independent implementation |
| `collections.Counter` and `defaultdict` | Independent implementation |
| `match` statements, `namedtuple` | Awareness |

### Live session plan

| Segment | Time | What happens |
|---|---:|---|
| Problem and intuition | 15 min | The two dashboard bugs: data that changed although nobody wrote to it, and a valid `0` treated as missing |
| Visual explanation and demo | 25 min | Names and objects; mutable versus immutable; truthiness and `is`; choosing a collection, with a live timing of list versus set lookups |
| Guided coding | 45 min | Comprehensions, slicing, sorting, `Counter` and `defaultdict`, building up to the morning-summary pipeline in the deep-dive notebook |
| Debugging challenge | 20 min | The deep-dive notebook's "report that lies": three bugs, found with Observe → Hypothesize → Inspect → Fix → Verify |
| Recap and assignment briefing | 15 min | Key takeaways; set up the workbook project and run the checker together |

## 7. Live demonstration

The instructor will:

1. Change a dict through one name and show the change through another, then use `id()` and `is` to prove there is one object.
2. Show a shallow copy leaking a change through a shared nested list, and fix it with `copy.deepcopy()`.
3. Contrast `+=` on a list with `+=` on an integer, using the mutable-versus-immutable diagram.
4. Demonstrate `0` disappearing from a truthiness filter, and fix it with `is None`.
5. Time `x in list` against `x in set` on 100,000 ticket IDs.
6. Build the per-team summary step by step: dedupe with a set, group with `defaultdict`, aggregate with comprehensions, rank with a tuple sort key.

## 8. Guided exercises

Work through the notebooks in this order, during and after the session:

1. [`notebooks/01-concepts.ipynb`](notebooks/01-concepts.ipynb): names and objects, mutability, scalar types, truthiness, loops, comprehensions and slicing.
   - **Aliasing in action:** predict what a change through a second name does.
   - **Strings are immutable:** find the bug in a cleanup line that does nothing.
   - **Debugging lab:** a list that loses items you never removed.
2. [`notebooks/03-collections-deep-dive.ipynb`](notebooks/03-collections-deep-dive.ipynb): choosing and using list, tuple, dict and set.
   - **List versus set timing:** measure the cost of the wrong choice.
   - **Morning summary pipeline:** dedupe, filter, group, aggregate and rank real-looking records.
   - **Debugging lab:** a report helper with three bugs.
3. [`notebooks/02-practice-quiz.ipynb`](notebooks/02-practice-quiz.ipynb): 12 self-check questions on everything above.

## 9. Independent assignment

[**Workbook: the morning incident summary**](workbook/assignment.md) (*Independent*: no AI coding assistant)

Clean a messy export of 16 synthetic incident tickets (inconsistent case and whitespace, duplicate records, blank assignees), then report open tickets, SLA breaches and unassigned work per team, plus the most common tags. You implement eight small functions against provided starter files, and a checker script tells you which requirements pass.

## 10. Expected deliverables

- A uv project containing `ticket_summary.py` with every function implemented, plus the unchanged `sample_tickets.py` and `check_summary.py`.
- `uv run check_summary.py` reporting 16 of 16 checks passed.
- `uv run ticket_summary.py` printing the report shown in the workbook.
- `NOTES.md` with your data-quality findings, bug analysis and reflection.

## 11. Common mistakes

| Mistake | Instead |
|---|---|
| `b = a` to copy a list or dict | `a.copy()`, or `copy.deepcopy(a)` for nested data |
| Calling a string method and discarding the result | `name = name.strip()`, since strings are immutable |
| `if not value:` when `0` or `""` is a valid value | `if value is None:` |
| `x is 1000` or `name is "platform"` | `==` for values; `is` only for `None` and sentinels |
| `for i in range(len(items))` | `for item in items`, `enumerate()`, `zip()` |
| Removing items from a list while looping over it | Build a new list with a comprehension |
| `x in big_list` inside a loop | Build a set once, before the loop |
| `items = items.sort()` | `items.sort()` alone, or `items = sorted(items)` |
| `dict.fromkeys(keys, [])` | `{k: [] for k in keys}` or `defaultdict(list)` |
| `{}` for an empty set | `set()` |
| A helper that sorts or edits the caller's data | Return new data; leave inputs untouched |

## 12. Reading resources

Curated official documentation for this session: [`resources/references.md`](resources/references.md).

## 13. Reflection questions

1. Which Python behaviour from this session would most likely have caused a production bug in your first month, coming from your main language?
2. Java and C# distinguish value types from reference types. Python doesn't. What does Python lose and gain with "everything is an object"?
3. When is mutating data in place the right choice, despite the risks? What would you document in that case?
4. Comprehensions versus loops: where do you draw the line, and how would you explain that line in a code review?

## 14. Interview questions

Practise answering these out loud, in two minutes or less each:

1. Is Python pass-by-value or pass-by-reference? Explain precisely what happens when you pass a list to a function.
2. What's the difference between a shallow copy and a deep copy? Give an example where the difference causes a bug.
3. Why can't a list be a dictionary key, while a tuple can? Is every tuple hashable?
4. When would you use `is` instead of `==`?
5. You need to check whether each of 1 million events has an ID you've already processed. Which data structure do you use, and why?
6. What does `dict.fromkeys(["a", "b"], [])` return, and what goes wrong if you then append to one of the lists?
7. Explain the difference between `sorted(items)` and `items.sort()`. Which would you use inside a helper function, and why?

## 15. Next-session preparation

**Session 03: Functions, Exceptions, Files and JSON** covers designing functions (positional, keyword-only and default arguments, including the mutable-default trap that follows directly from this session), type hints, exceptions and tracebacks, context managers, and reading and writing JSON files.

Before the session:

- Finish the Session 02 workbook. Session 03's assignment reads ticket data from JSON files instead of a Python module, and your functions will carry over.
- Revisit Part 1 of `01-concepts.ipynb` (names and objects). The mutable-default-argument trap in Session 03 is the same idea in a new place.
