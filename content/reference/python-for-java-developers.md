# Python for Java Developers

Python will feel smaller than Java: fewer keywords, no compilation step, no build files to speak of. The bigger change is in what the language checks for you. Java's compiler rejects a wrong type before the program runs; Python's interpreter finds it when the line runs, so tests, type hints and validation at the edges do the job the compiler did. This page maps what you know to how Python does it, and flags the traps.

## The big differences

| Java | Python | What it means for you |
|---|---|---|
| Compiled to bytecode, type-checked | Compiled to bytecode at run time, **not** type-checked | Type errors appear when the line runs: test more, and read tracebacks |
| Static types everywhere | Optional **type hints**, ignored at run time | `def f(x: int)` accepts a string. Hints document intent; tools like mypy check them |
| Braces and semicolons | **Indentation** is the block structure | Four spaces; mixing tabs and spaces is an error |
| `null`, `Optional<T>` | `None`; hint it as `T \| None` | `if value is None:` |
| Everything inside a class | Functions and variables at module level are normal | Not every function needs a class |
| `public` / `private` | Conventions: `_name` is internal | Nothing is enforced; respect the underscore |
| Checked exceptions | All exceptions unchecked | Document what you raise; catch what you can handle |
| Maven or Gradle | `uv` and `pyproject.toml` | [`uv-cheatsheet.md`](uv-cheatsheet.md) |

## Variables, types and collections (Session 02)

```java
List<String> teams = new ArrayList<>(List.of("network", "platform"));
Map<String, Integer> open = new HashMap<>();
open.put("network", 3);
int count = open.getOrDefault("dns", 0);
```

```python
teams = ["network", "platform"]  # list
open_tickets = {"network": 3}  # dict
count = open_tickets.get("dns", 0)
print(teams, count)
```

| Java | Python |
|---|---|
| `ArrayList<T>` | `list` |
| `HashMap<K, V>` | `dict` (keeps insertion order) |
| `HashSet<T>` | `set` |
| `List.of(...)`, records of fixed values | `tuple` |
| `int`, `long`, `BigInteger` | `int`, with no overflow |
| `str.equals(other)` | `str == other` (`==` compares values; `is` compares identity) |

## Streams and comprehensions

```java
List<String> ids = tickets.stream()
    .filter(t -> t.team().equals("network"))
    .map(Ticket::id)
    .toList();
```

```python
tickets = [{"id": "INC-1", "team": "network"}, {"id": "INC-2", "team": "dns"}]
ids = [t["id"] for t in tickets if t["team"] == "network"]
by_team = {t["team"]: t["id"] for t in tickets}
print(ids, by_team, sum(1 for t in tickets if t["team"] == "dns"))
```

A comprehension is the usual Python form of `filter` + `map`. For grouping, `collections.Counter`, `defaultdict` and `itertools.groupby` replace most `Collectors`.

## Traps for Java developers

- **References work as in Java**, but there are no primitives: `a = b` makes two names for one object, and a list passed to a function can be changed by it.
- **Mutable default arguments** (`def f(tags=[])`) are created once and shared between calls. Use `None` and create the list inside.
- **Integer division:** `7 / 2` is `3.5`; `7 // 2` is `3`.
- **Truthiness:** empty strings and collections, `0` and `None` are false in an `if`. `if not items:` is idiomatic.
<!-- release:2 -->

## Functions and exceptions (Session 03)

Python has no method overloading. Default values and keyword arguments do the job:

```python
def find(
    tickets: list[dict], *, team: str | None = None, limit: int = 50
) -> list[dict]:
    return [t for t in tickets if team is None or t["team"] == team][:limit]


print(find([{"team": "dns"}], team="dns"))
```

| Java | Python |
|---|---|
| `try { } catch (IOException e) { } finally { }` | `try: ... except OSError as e: ... finally: ...` |
| `throw new IllegalArgumentException(msg, cause)` | `raise ValueError(msg) from cause` |
| try-with-resources | `with open(path, encoding="utf-8") as f:` |
| `throws` clauses | none: document exceptions in the docstring |

## Classes, records and interfaces (Session 04)

```java
public record Ticket(String id, String team) {}

public interface Notifier { void send(String message); }
```

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)  # like a record: __init__, __eq__, __repr__, immutability
class Ticket:
    id: str
    team: str


class Notifier(Protocol):  # structural: any class with send() matches, no "implements"
    def send(self, message: str) -> None: ...


class PrintNotifier:
    def send(self, message: str) -> None:
        print(message)


def alert(notifier: Notifier, ticket: Ticket) -> None:
    notifier.send(f"{ticket.id} for {ticket.team}")


alert(PrintNotifier(), Ticket("INC-1", "network"))
```

- **No getters and setters:** use attributes, and `@property` when a value needs computing or checking.
- **`self` is explicit** in every method's parameters.
- **Composition over inheritance** is even more natural: protocols mean you rarely need a base class.

## Packages and tests (Session 04)

| Java | Python |
|---|---|
| `package com.orbital.reports;` and folders | A folder with `__init__.py` is a package: `from incident_report.models import Ticket` |
| `public static void main` | A function registered under `[project.scripts]`, run with `uv run <name>` |
| JUnit 5, `@Test`, `assertEquals` | pytest: plain functions named `test_*`, plain `assert` |
| `@BeforeEach`, dependency injection in tests | pytest **fixtures** |
| `@ParameterizedTest` | `@pytest.mark.parametrize` |
| Mockito | `unittest.mock`, pytest's `monkeypatch`, or a small fake class |

See [`project-structure.md`](project-structure.md) and [`python-for-qa-engineers.md`](python-for-qa-engineers.md).
<!-- /release:2 -->
<!-- release:3 -->

## HTTP and validation (Sessions 05 and 06)

| Java | Python |
|---|---|
| `java.net.http.HttpClient`, OkHttp | HTTPX (`httpx.Client`), always with a timeout |
| Jackson (`ObjectMapper`) | the `json` module, or Pydantic's `model_validate_json` |
| Bean Validation (`@NotNull`, `@Size`) | Pydantic field types and constraints, `@field_validator` |
| `@ConfigurationProperties` | pydantic-settings' `BaseSettings` |

See [`pydantic-patterns.md`](pydantic-patterns.md).
<!-- /release:3 -->
<!-- release:4 -->

## Web services and concurrency (Sessions 07 and 08)

| Spring Boot | FastAPI |
|---|---|
| `@RestController`, `@GetMapping("/tickets/{id}")` | `@app.get("/tickets/{ticket_id}")` on a function |
| `@RequestBody Ticket ticket` with `@Valid` | a Pydantic parameter: validated automatically, 422 if invalid |
| `@Autowired` and beans | `Depends(...)` |
| `@ControllerAdvice` | `app.add_exception_handler(...)` |
| Springdoc OpenAPI | built in: `/docs` |
| MockMvc | `fastapi.testclient.TestClient` |

| Java concurrency | Python |
|---|---|
| Threads, virtual threads | Threads exist, but the GIL lets one run Python code at a time: good for I/O, not for CPU work |
| `CompletableFuture` | `async def` / `await`, run by `asyncio`'s event loop on one thread |
| `allOf(...)` | `asyncio.gather(...)` or a `TaskGroup` |
| `ExecutorService` for CPU work | `concurrent.futures.ProcessPoolExecutor` |

See [`fastapi-patterns.md`](fastapi-patterns.md) and [`async-await.md`](async-await.md).
<!-- /release:4 -->

## Further reading

- [The Python Tutorial](https://docs.python.org/3.13/tutorial/): read sections 3 to 9 in an evening.
- [`python-cheatsheet.md`](python-cheatsheet.md), and the [glossary](glossary.md).
