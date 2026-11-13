# Python for JavaScript and TypeScript Developers

Python and JavaScript are both dynamic, garbage-collected and comfortable with functions as values, and both have `async`/`await` on an event loop. The differences are in the details you type every day: truthiness, equality, `None` instead of two kinds of nothing, indentation instead of braces, and a standard library that does far more out of the box. TypeScript developers will recognise type hints, with one catch: nothing checks them unless you run a tool, and nothing at all at run time.

## The big differences

| JavaScript / TypeScript | Python | What it means for you |
|---|---|---|
| `{ }` blocks, optional semicolons | **Indentation** | Four spaces per level |
| `null` **and** `undefined` | Only `None` | A missing dict key raises `KeyError`: use `d.get("key")` |
| `==` coerces, `===` doesn't | `==` never coerces between types | `1 == "1"` is `False`; there's no `===` |
| `[]` and `{}` are truthy | Empty collections are **falsy** | `if not items:` means "empty" |
| `obj.key` for every object | `obj.key` for attributes, `d["key"]` for dict entries | JSON becomes dicts: use `["key"]` |
| TypeScript types, checked by `tsc` | Type hints, checked only by tools such as mypy | Validate external data at run time (Pydantic, from Session 06) |
| npm, `package.json`, `node_modules` | uv, `pyproject.toml`, `.venv` | [`uv-cheatsheet.md`](uv-cheatsheet.md) |
| `let` / `const` | Plain assignment; `UPPER_CASE` names are constants by convention | Nothing prevents reassignment |

## Collections and array methods (Session 02)

```javascript
const ids = tickets.filter(t => t.team === "network").map(t => t.id);
const total = tickets.reduce((sum, t) => sum + t.hours, 0);
const { id, team } = tickets[0];
```

```python
tickets = [
    {"id": "INC-1", "team": "network", "hours": 3},
    {"id": "INC-2", "team": "dns", "hours": 5},
]
ids = [t["id"] for t in tickets if t["team"] == "network"]
total = sum(t["hours"] for t in tickets)
first_id, first_team = tickets[0]["id"], tickets[0]["team"]  # no object destructuring
head, *rest = [1, 2, 3]  # but sequences unpack
print(ids, total, first_id, first_team, head, rest)
```

| JavaScript | Python |
|---|---|
| `Array` | `list` |
| plain object, `Map` | `dict` |
| `Set` | `set` |
| `arr.length` | `len(arr)` |
| `arr.includes(x)`, `key in obj` | `x in items`, `key in mapping` |
| `arr.slice(1, 3)` | `items[1:3]` |
| `JSON.parse`, `JSON.stringify` | `json.loads`, `json.dumps` |
| `` `Hello ${name}` `` | `f"Hello {name}"` |
| `...spread` | `[*a, *b]`, `{**a, **b}`, or `a \| b` for dicts |

## Traps for JavaScript developers

- **Mutable default arguments** (`def f(tags=[])`) are evaluated once and shared between calls. Use `None`.
- **Integers are integers:** `7 / 2` is `3.5`, `7 // 2` is `3`, and integers never lose precision.
- **No implicit globals**, but assigning to a name inside a function makes it local to that function. Reading it before assigning raises `UnboundLocalError`.
- **Sorting** is numeric for numbers: `sorted([10, 9, 1])` is `[1, 9, 10]`, not the string order JavaScript's default `sort()` gives.
<!-- release:2 -->

## Functions, errors and modules (Sessions 03 and 04)

| JavaScript | Python |
|---|---|
| `function f({team, limit = 50} = {})` | `def f(*, team=None, limit=50)`: keyword-only arguments |
| `(...args)` | `*args`, and `**kwargs` for named extras |
| `throw new Error(msg, {cause})` | `raise ValueError(msg) from cause` |
| `try / catch (e) / finally` | `try / except ValueError as e / finally` |
| `import { Ticket } from "./models.js"` | `from incident_report.models import Ticket` |
| `export` | Every top-level name is importable; `_name` signals "internal" |
| classes with `constructor` and `this` | classes with `__init__` and an explicit `self`; `@dataclass` writes `__init__` for you |
| Jest / Vitest, `expect(x).toBe(y)` | pytest, plain `assert x == y` |
| `jest.fn()`, `vi.mock` | `unittest.mock`, `monkeypatch`, or a small fake class |

See [`project-structure.md`](project-structure.md) and [`python-for-qa-engineers.md`](python-for-qa-engineers.md).
<!-- /release:2 -->
<!-- release:3 -->

## HTTP and validation (Sessions 05 and 06)

| JavaScript / TypeScript | Python |
|---|---|
| `fetch`, axios | HTTPX: `httpx.Client` or `httpx.AsyncClient`, always with a timeout |
| Zod schemas, `schema.parse(data)` | Pydantic models, `Model.model_validate(data)` |
| `process.env.API_KEY`, dotenv | `os.environ["API_KEY"]`, or pydantic-settings with `.env` |

See [`pydantic-patterns.md`](pydantic-patterns.md).
<!-- /release:3 -->
<!-- release:4 -->

## Web services and async (Sessions 07 and 08)

| Express / Fastify / NestJS | FastAPI |
|---|---|
| `app.get("/tickets/:id", handler)` | `@app.get("/tickets/{ticket_id}")` |
| Validation middleware (Zod, class-validator) | Pydantic parameters: 422 for invalid input, automatically |
| Error-handling middleware | `app.add_exception_handler(...)` |
| NestJS providers | `Depends(...)` |
| supertest | `TestClient` |

Python's `asyncio` is close to Node's event loop, with three differences:

- **Node is async by default; Python isn't.** Most Python libraries are synchronous, and a blocking call (`time.sleep`, a sync HTTP client) inside `async def` stalls every other task.
- **A coroutine doesn't start until it's awaited or scheduled.** A Promise starts immediately.
- **`Promise.all` is `asyncio.gather`**, and `Promise.race` with a timer is `asyncio.timeout(...)`.

See [`fastapi-patterns.md`](fastapi-patterns.md) and [`async-await.md`](async-await.md).
<!-- /release:4 -->

## Further reading

- [The Python Tutorial](https://docs.python.org/3.13/tutorial/), sections 3 to 9.
- [`python-cheatsheet.md`](python-cheatsheet.md), and the [glossary](glossary.md).
