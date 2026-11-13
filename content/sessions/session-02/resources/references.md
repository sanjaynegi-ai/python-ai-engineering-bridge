# Session 02: References

Official documentation first. Each link says *why* it's worth your time, so you can pick what you need instead of reading everything.

## The language

| Resource | Read it for |
|---|---|
| [Python tutorial: An Informal Introduction](https://docs.python.org/3/tutorial/introduction.html) | A concise overview of numbers, strings, slicing and lists |
| [Python tutorial: More Control Flow Tools](https://docs.python.org/3/tutorial/controlflow.html) | `if`, `for`, `range`, `break`/`continue`/`else` on loops, and a first look at `match` |
| [Python tutorial: Data Structures](https://docs.python.org/3/tutorial/datastructures.html) | Lists, tuples, sets, dicts, comprehensions and looping techniques, all in one chapter |
| [Data model: objects, values and types](https://docs.python.org/3/reference/datamodel.html#objects-values-and-types) | The precise definition of identity, type and mutability that this session is built on |
| [Naming and binding](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding) | What assignment really does: binding names to objects |
| [Programming FAQ: why did changing list `y` also change list `x`?](https://docs.python.org/3/faq/programming.html#why-did-changing-list-y-also-change-list-x) | The official explanation of aliasing, with the same examples you'll meet in practice |
| [Programming FAQ: how do I write a function with output parameters?](https://docs.python.org/3/faq/programming.html#how-do-i-write-a-function-with-output-parameters-call-by-reference) | How argument passing works, and the idiomatic alternatives |

## Built-in types

| Resource | Read it for |
|---|---|
| [Truth value testing](https://docs.python.org/3.13/library/stdtypes.html#truth-value-testing) | The exact list of falsy values |
| [Comparisons](https://docs.python.org/3.13/library/stdtypes.html#comparisons) | `==` versus `is`, and chained comparisons |
| [Numeric types](https://docs.python.org/3.13/library/stdtypes.html#numeric-types-int-float-complex) | `/`, `//`, `%`, `round()` and friends, with their precise rules |
| [Common sequence operations](https://docs.python.org/3.13/library/stdtypes.html#common-sequence-operations) | Slicing, `in`, `len`, `min`/`max`, and footnotes on edge cases |
| [String methods](https://docs.python.org/3.13/library/stdtypes.html#string-methods) | `strip`, `split`, `join`, `startswith` and the rest |
| [Format specification mini-language](https://docs.python.org/3/library/string.html#formatspec) | Everything after the colon in an f-string: `{x:>10}`, `{x:,.2f}` |
| [Mapping types: `dict`](https://docs.python.org/3.13/library/stdtypes.html#mapping-types-dict) | `get`, `setdefault`, `fromkeys`, `|` merging, and view objects |
| [Set types](https://docs.python.org/3.13/library/stdtypes.html#set-types-set-frozenset) | Set operations and their operator forms |
| [Sorting techniques](https://docs.python.org/3/howto/sorting.html) | `key=` functions, multi-key sorts and sort stability |

## Standard library

| Resource | Read it for |
|---|---|
| [`collections`: `Counter`, `defaultdict` and more](https://docs.python.org/3/library/collections.html) | Counting and grouping without hand-written bookkeeping |
| [`copy`: shallow and deep copy](https://docs.python.org/3/library/copy.html) | When `copy.copy` and `copy.deepcopy` differ, and how deep copy handles cycles |
| [Built-in functions](https://docs.python.org/3/library/functions.html) | `enumerate`, `zip`, `sorted`, `sum`, `any`, `all`, `max` with `default=`: worth one skim |
| [`timeit`](https://docs.python.org/3/library/timeit.html) | Measuring small snippets reliably, as in the list-versus-set comparison |

## Performance

| Resource | Read it for |
|---|---|
| [Python wiki: TimeComplexity](https://wiki.python.org/python/language/TimeComplexity.html) | Big-O costs of list, dict and set operations in CPython |

## Style

| Resource | Read it for |
|---|---|
| [PEP 8: Programming recommendations](https://peps.python.org/pep-0008/#programming-recommendations) | The official guidance on `is None`, truthiness checks and more |
| [PEP 20: The Zen of Python](https://peps.python.org/pep-0020/) | Nineteen lines that explain a lot of Python's design choices. Also available as `import this` |

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
