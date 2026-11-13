# Python for QA and Automation Engineers

If you've built test frameworks with Selenium, TestNG, JUnit, Cypress or Playwright, you already think the way this course wants: in requirements, edge cases and evidence. This page maps that experience onto **pytest**, Python's de facto test runner, and points to the parts of the course where your skills matter most.

## pytest in one page (Session 04)

```python
import pytest


def priority_of(text: str) -> int:
    if not text.startswith("P") or text[1:] not in {"1", "2", "3", "4"}:
        raise ValueError(f"not a priority: {text!r}")
    return int(text[1:])


def test_a_valid_priority():
    assert priority_of("P2") == 2  # a plain assert: pytest shows both sides on failure


@pytest.mark.parametrize(
    ("text", "expected"),
    [("P1", 1), ("P4", 4)],
    ids=["highest", "lowest"],
)
def test_boundaries(text, expected):
    assert priority_of(text) == expected


@pytest.mark.parametrize("bad", ["P0", "P5", "p1", "", "P"])
def test_invalid_priorities_are_rejected(bad):
    with pytest.raises(ValueError, match="not a priority"):
        priority_of(bad)


def test_floats_need_approx():
    assert 0.1 + 0.2 == pytest.approx(0.3)
```

| TestNG / JUnit | pytest |
|---|---|
| `@Test` methods in a class | Functions named `test_*` in files named `test_*.py` (classes optional) |
| `assertEquals(expected, actual)` | `assert actual == expected` |
| `@DataProvider`, `@ParameterizedTest` | `@pytest.mark.parametrize`, with `ids` for readable names |
| `expectedExceptions` | `with pytest.raises(SomeError, match="..."):` |
| `@BeforeMethod` / `@AfterMethod` | A **fixture**: setup before `yield`, teardown after |
| `@BeforeClass` | A fixture with `scope="module"` or `scope="session"` |
| Groups | Markers: `@pytest.mark.slow`, selected with `-m "not slow"` |
| testng.xml suites | Folders, `-k` expressions and markers; configuration in `pyproject.toml` |

## Fixtures

```python
import json

import pytest


@pytest.fixture
def export_file(tmp_path):  # tmp_path: a fresh temporary folder for each test
    path = tmp_path / "tickets.json"
    path.write_text(json.dumps([{"id": "INC-1", "team": "network"}]), encoding="utf-8")
    yield path  # the test runs here
    # teardown would go here; tmp_path is cleaned up by pytest


def test_the_export_has_one_ticket(export_file):
    assert len(json.loads(export_file.read_text(encoding="utf-8"))) == 1


def test_environment_is_isolated(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "debug")  # undone automatically after the test
    import os

    assert os.environ["LOG_LEVEL"] == "debug"
```

Built-in fixtures worth knowing: `tmp_path` (files), `monkeypatch` (environment variables, attributes), `capsys` (printed output), `caplog` (log records). Shared fixtures go in `conftest.py`, which pytest loads automatically.

## Running tests

| I want to... | Run |
|---|---|
| Run everything | `uv run pytest` |
| Stop at the first failure | `uv run pytest -x` |
| Re-run only what failed last time | `uv run pytest --lf` |
| Run tests whose names match | `uv run pytest -k "priority and not invalid"` |
| One test | `uv run pytest tests/test_models.py::test_a_valid_priority` |
| See print output | `uv run pytest -s` |
| See why tests were skipped | `uv run pytest -ra` |

## Test doubles

Prefer a small **fake** that behaves like the real thing (a class with the same methods) over patching. When you must replace something in place, `monkeypatch.setattr(module, "name", replacement)` undoes itself after the test; `unittest.mock.Mock` records calls. The course uses fakes throughout: a fake asset inventory, a fake OpenAI API at the HTTP level, a hashing embedder.

## Where your experience pays off in the course

- **Acceptance tests are the specification** in every project: reading them closely is the fastest way to understand a requirement.
- **Mutation thinking:** the course's assessment runs your tests against broken versions of a function (Session 16). Ask "what bug would this test catch?" for each one you write.
- **Flaky tests:** time, order, randomness and shared state cause most of them, in Python as anywhere. Freeze or inject time; give every test its own data.
- **Browser automation** isn't part of this course, but both [Playwright](https://playwright.dev/python/) and [Selenium](https://www.selenium.dev/documentation/) have official Python bindings that use pytest.
<!-- release:3 -->

## Testing HTTP clients (Sessions 05 and 06)

```python
import httpx
import respx


@respx.mock
def test_a_server_error_is_reported():
    respx.get("https://assets.example.com/assets/vpn-ber").mock(
        return_value=httpx.Response(503, json={"error": "maintenance"})
    )
    with httpx.Client(base_url="https://assets.example.com", timeout=5) as client:
        response = client.get("/assets/vpn-ber")
    assert response.status_code == 503
```

`respx` intercepts HTTPX requests, so no test touches the network. Pydantic's `ValidationError` lists every invalid field: assert on `error.errors()` to check which rule fired.
<!-- /release:3 -->
<!-- release:4 -->

## Testing APIs (Sessions 07 and 08)

```python
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str) -> dict:
    if ticket_id != "INC-1":
        raise HTTPException(404, "no such ticket")
    return {"id": ticket_id}


def test_an_unknown_ticket_is_404():
    response = TestClient(app).get("/tickets/INC-9")
    assert response.status_code == 404
    assert response.json() == {"detail": "no such ticket"}
```

`TestClient` calls the application in-process: no server, no port. Async tests need `pytest-asyncio` and `@pytest.mark.asyncio`.
<!-- /release:4 -->

## Further reading

- [pytest: getting started](https://docs.pytest.org/en/stable/getting-started.html), [fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) and [parametrizing](https://docs.pytest.org/en/stable/how-to/parametrize.html).
- [`project-structure.md`](project-structure.md): where tests live in a project.
