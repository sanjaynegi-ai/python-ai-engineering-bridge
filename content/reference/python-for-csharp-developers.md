# Python for C# Developers

A lot will feel familiar: `async`/`await`, generics in type hints, properties, LINQ-like comprehensions, and a modern package manager. The big difference is the type system. C#'s compiler enforces types; Python's interpreter ignores type hints at run time, so validation at your program's edges (Pydantic, from Session 06) and tests take over that job. This page maps what you know, and flags the traps.

## The big differences

| C# | Python | What it means for you |
|---|---|---|
| Compiled, statically typed | Interpreted, dynamically typed, with optional hints | Wrong types fail when the line runs, not at build time |
| `{ }` blocks | **Indentation** | Four spaces per level |
| Nullable reference types, `?.`, `??` | `None`; `x if x is not None else default`; `value or default` for falsy values | There's no `?.`: check for `None` explicitly |
| Namespaces, `using` | Modules and packages, `import` | One file is one module |
| `public` / `private` / `internal` | Conventions: `_name` is internal | Not enforced |
| NuGet, `.csproj` | uv, `pyproject.toml` | [`uv-cheatsheet.md`](uv-cheatsheet.md) |
| `var` | Every variable is untyped by default | Hints are optional: `count: int = 0` |

## Collections and LINQ (Session 02)

```csharp
var open = tickets.Where(t => t.Team == "network").Select(t => t.Id).ToList();
var byTeam = tickets.GroupBy(t => t.Team).ToDictionary(g => g.Key, g => g.Count());
```

```python
from collections import Counter

tickets = [
    {"id": "INC-1", "team": "network"},
    {"id": "INC-2", "team": "network"},
    {"id": "INC-3", "team": "dns"},
]
open_ids = [t["id"] for t in tickets if t["team"] == "network"]
by_team = Counter(t["team"] for t in tickets)
print(open_ids, dict(by_team), any(t["team"] == "dns" for t in tickets))
```

| C# | Python |
|---|---|
| `List<T>` | `list` |
| `Dictionary<K, V>` | `dict` |
| `HashSet<T>` | `set` |
| Tuples, `record struct` | `tuple` |
| `Where` / `Select` | comprehensions |
| `Any` / `All` / `Count` / `Sum` | `any()`, `all()`, `len()`, `sum()` |
| `OrderBy(x => x.Key)` | `sorted(items, key=lambda x: x["key"])` |
| `GroupBy` | `Counter`, `defaultdict(list)`, `itertools.groupby` (on sorted data) |

## Traps for C# developers

- **No value types:** everything is an object reference. `b = a` for a list gives two names for one list.
- **Mutable default arguments** (`def f(tags=[])`) are shared between calls. Use `None`.
- **`==` versus `is`:** `==` is value equality (like `Equals`); `is` is reference identity (like `ReferenceEquals`). Use `is` only with `None`.
- **Strings:** f-strings (`f"{name}"`) are interpolated strings (`$"{name}"`). Two string literals side by side are joined, so a missing comma in `["vpn" "dns"]` silently gives `["vpndns"]`.
<!-- release:2 -->

## Methods, exceptions and resources (Session 03)

| C# | Python |
|---|---|
| Overloads, optional and named parameters | Default values and keyword arguments: `def find(tickets, *, team=None)` |
| `params T[]` | `*args`; `**kwargs` for named extras |
| `throw new ArgumentException(msg, inner)` | `raise ValueError(msg) from inner` |
| `catch (IOException e) when (...)` | `except OSError as e:` then an `if` |
| `using var file = ...` | `with open(path, encoding="utf-8") as file:` |

## Classes, records and interfaces (Session 04)

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)  # like a positional record: equality, ToString, immutability
class Ticket:
    id: str
    team: str

    @property
    def is_network(self) -> bool:  # like a get-only computed property
        return self.team == "network"


class Clock(Protocol):  # like an interface, but matched by shape, not by declaration
    def now_hour(self) -> int: ...


class FixedClock:
    def now_hour(self) -> int:
        return 9


def greeting(clock: Clock) -> str:
    return "morning" if clock.now_hour() < 12 else "afternoon"


print(Ticket("INC-1", "network").is_network, greeting(FixedClock()))
```

| C# | Python |
|---|---|
| xUnit / NUnit, `[Fact]`, `Assert.Equal` | pytest: functions named `test_*`, plain `assert` |
| `[Theory]` with `[InlineData]` | `@pytest.mark.parametrize` |
| Moq | `unittest.mock`, `monkeypatch`, or a fake class matching a protocol |
| Test fixtures, `IClassFixture` | pytest fixtures |

See [`project-structure.md`](project-structure.md).
<!-- /release:2 -->
<!-- release:3 -->

## HTTP, JSON and validation (Sessions 05 and 06)

| .NET | Python |
|---|---|
| `HttpClient` (one shared instance) | `httpx.Client` (one per application), always with a timeout |
| `System.Text.Json` | `json`, or Pydantic's `model_validate_json` and `model_dump_json` |
| Data annotations (`[Required]`, `[Range]`) | Pydantic types and constraints, `@field_validator`, `@model_validator` |
| `IOptions<T>`, `appsettings.json` | pydantic-settings' `BaseSettings`, from environment variables and `.env` |

See [`pydantic-patterns.md`](pydantic-patterns.md).
<!-- /release:3 -->
<!-- release:4 -->

## Web APIs and async (Sessions 07 and 08)

| ASP.NET Core | FastAPI |
|---|---|
| Minimal APIs: `app.MapGet("/tickets/{id}", ...)` | `@app.get("/tickets/{ticket_id}")` |
| Model binding and validation | Pydantic parameters: invalid input is a 422 automatically |
| Built-in dependency injection | `Depends(...)`, overridden in tests with `app.dependency_overrides` |
| Exception-handling middleware | `app.add_exception_handler(...)` |
| Swashbuckle / OpenAPI | built in, at `/docs` |
| `WebApplicationFactory` | `TestClient` |

`async`/`await` will feel like home, with three differences:

| C# | Python |
|---|---|
| `Task<T>` starts running when created | A coroutine does **nothing** until it's awaited or scheduled |
| `Task.WhenAll` | `asyncio.gather(...)` or `asyncio.TaskGroup` |
| A thread pool runs continuations | One event loop on one thread; a blocking call (`time.sleep`, `requests`) stalls everything |
| `Task.Run` for CPU work | A process pool: the GIL lets only one thread run Python code at a time |

See [`fastapi-patterns.md`](fastapi-patterns.md) and [`async-await.md`](async-await.md).
<!-- /release:4 -->

## Further reading

- [The Python Tutorial](https://docs.python.org/3.13/tutorial/), sections 3 to 9.
- [`python-cheatsheet.md`](python-cheatsheet.md), and the [glossary](glossary.md).
