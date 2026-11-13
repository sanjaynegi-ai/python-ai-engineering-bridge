# Python Cheatsheet

A one-page reminder of the Python the course uses, for Python 3.13. It doesn't teach: each section points to the session that does. Run any example with `uv run python` in the course repository.

## Running code

| Task | Command |
|---|---|
| Run a script | `uv run python report.py` |
| Run a module or a project's command | `uv run python -m incident_report`, `uv run incident-report` |
| An interactive prompt | `uv run python` (leave with `exit()`) |
| Run the tests | `uv run pytest` |

## Values and types (Session 02)

```python
count = 3  # int: any size
ratio = 0.75  # float
name = "vpn-ber"  # str: immutable
ok = True  # bool: True and False, capitalised
nothing = None  # the single "no value" object

print(type(count), isinstance(ratio, float))
print(7 / 2, 7 // 2, 7 % 2, 2**10)  # 3.5 3 1 1024
```

- `==` compares values; `is` compares identity. Use `is` only with `None` (`if value is None:`).
- Falsy values: `None`, `False`, `0`, `0.0`, `""`, and empty collections. Everything else is truthy.
- Type hints (`count: int = 3`) document intent; Python doesn't enforce them at run time.

## Strings

```python
team, hours = "network", 4.5
print(f"{team} took {hours:.1f} h")  # f-string, with a format spec
print("  P1 ".strip(), "a,b,c".split(","), "-".join(["x", "y"]))
print("vpn" in "office vpn outage", "INC-42".startswith("INC-"))
print(
    """triple quotes
span lines"""
)
```

## Collections (Session 02)

| Type | Literal | Ordered | Mutable | Typical use |
|---|---|---|---|---|
| `list` | `[1, 2, 3]` | yes | yes | A sequence you'll change |
| `tuple` | `(1, 2)` | yes | no | A fixed group of values; a dict key |
| `dict` | `{"id": 1}` | insertion order | yes | Lookup by key |
| `set` | `{"vpn", "dns"}` | no | yes | Membership, uniqueness |

```python
tickets = [{"id": "INC-1", "team": "network"}, {"id": "INC-2", "team": "platform"}]
tickets.append({"id": "INC-3", "team": "network"})
by_id = {t["id"]: t for t in tickets}  # dict comprehension
network = [t["id"] for t in tickets if t["team"] == "network"]  # list comprehension
teams = {t["team"] for t in tickets}  # set comprehension
print(network, sorted(teams), by_id.get("INC-9", "missing"))

for index, ticket in enumerate(tickets, start=1):
    print(index, ticket["id"])
for key, value in by_id["INC-1"].items():
    print(key, value)
```

## Slicing

```python
items = ["a", "b", "c", "d", "e"]
print(items[0], items[-1], items[1:3], items[:2], items[::2], items[::-1])
```

## Control flow

```python
priority = "P2"
if priority == "P1":
    action = "page"
elif priority in ("P2", "P3"):
    action = "queue"
else:
    action = "ignore"

match priority:  # structural pattern matching
    case "P1":
        label = "critical"
    case _:
        label = "normal"

while False:
    pass
print(action, label)
```
<!-- release:2 -->

## Functions (Session 03)

```python
def summarise(
    tickets: list[dict], *, team: str | None = None, limit: int = 10
) -> list[str]:
    """Arguments after * must be passed by name: summarise(tickets, team="network")."""
    chosen = [t for t in tickets if team is None or t["team"] == team]
    return [t["id"] for t in chosen[:limit]]


def add_tag(tag: str, tags: list[str] | None = None) -> list[str]:
    """Never use a mutable default such as tags=[]: it's shared between calls."""
    tags = [] if tags is None else tags
    tags.append(tag)
    return tags


print(summarise([{"id": "INC-1", "team": "network"}], team="network"), add_tag("vpn"))
```

## Exceptions (Session 03)

```python
class TicketError(Exception):
    """A domain error: subclass Exception, not BaseException."""


def parse_priority(text: str) -> int:
    try:
        number = int(text.removeprefix("P"))
    except ValueError as error:
        raise TicketError(f"not a priority: {text!r}") from error  # keep the cause
    if not 1 <= number <= 4:
        raise TicketError(f"priority out of range: {text!r}")
    return number


try:
    parse_priority("P9")
except TicketError as error:
    print("rejected:", error)
finally:
    print("always runs")
```

Catch the exceptions you expect and can handle; let the rest propagate. Never write a bare `except:`.

## Files and JSON (Session 03)

```python
import json
import tempfile
from pathlib import Path

folder = Path(tempfile.mkdtemp())
path = folder / "tickets.json"
path.write_text(json.dumps([{"id": "INC-1"}], indent=2), encoding="utf-8")

with path.open(encoding="utf-8") as file:  # closed automatically
    data = json.load(file)
print(data, path.name, path.suffix, path.exists())
```

Always pass `encoding="utf-8"`: on Windows, Python 3.13's default is still the system code page.

## Classes and dataclasses (Session 04)

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Ticket:
    id: str
    team: str
    tags: list[str] = field(default_factory=list)  # a fresh list per instance

    @property
    def is_network(self) -> bool:
        return self.team == "network"


ticket = Ticket("INC-1", "network")
print(ticket, ticket.is_network, ticket == Ticket("INC-1", "network"))
```

## Modules and imports (Session 04)

```text
src/incident_report/
├── __init__.py          makes the folder a package
├── models.py            from incident_report.models import Ticket
└── cli.py               def main() -> int: ...   (the entry point)
```

```python
import logging  # standard library first
from collections import Counter

print(Counter(["vpn", "dns", "vpn"]).most_common(1))
logger = logging.getLogger(__name__)  # one logger per module
```

Use absolute imports (`from incident_report.models import Ticket`), run code with `uv run`, and keep the `src/` layout: see [`project-structure.md`](project-structure.md).
<!-- /release:2 -->

## Further reading

- [The Python Tutorial](https://docs.python.org/3.13/tutorial/), for anything this page skips.
- [Built-in types](https://docs.python.org/3.13/library/stdtypes.html) and [built-in functions](https://docs.python.org/3.13/library/functions.html).
- [`python-for-java-developers.md`](python-for-java-developers.md), [`python-for-csharp-developers.md`](python-for-csharp-developers.md) and [`python-for-javascript-developers.md`](python-for-javascript-developers.md): Python compared with the language you know.
