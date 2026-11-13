# async and await

Asynchronous Python lets one thread wait for many slow things at once (HTTP calls, database queries, LLM requests) instead of waiting for them one after another. It doesn't make CPU work faster. Session 08 teaches the model; this page is the reference.

## The model in four sentences

1. `async def` defines a **coroutine function**; calling it creates a coroutine object, which does **nothing** until it's awaited or scheduled as a task.
2. `await` pauses the current coroutine until the awaited one finishes, and lets the **event loop** run others meanwhile.
3. The event loop runs on **one thread**: while one coroutine waits for I/O, another runs, but only one runs Python code at any moment.
4. So a coroutine must never **block** (with `time.sleep`, a synchronous HTTP client or a long computation): that stops every other coroutine too.

## Concurrency with `gather` and `TaskGroup`

```python
import asyncio
import time


async def fetch_assets(team: str, seconds: float) -> str:
    await asyncio.sleep(seconds)  # stands in for an HTTP call
    return f"{team}: ok"


async def main() -> None:
    start = time.perf_counter()
    one_by_one = [await fetch_assets(t, 0.2) for t in ("network", "dns", "platform")]
    sequential = time.perf_counter() - start

    start = time.perf_counter()
    together = await asyncio.gather(
        *(fetch_assets(t, 0.2) for t in ("network", "dns", "platform"))
    )
    concurrent = time.perf_counter() - start

    print(
        one_by_one == together, f"concurrent was faster: {concurrent < sequential / 2}"
    )

    async with (
        asyncio.TaskGroup() as group
    ):  # Python 3.11+: if one task fails, the rest are cancelled
        first = group.create_task(fetch_assets("network", 0.1))
        second = group.create_task(fetch_assets("dns", 0.1))
    print(first.result(), second.result())


asyncio.run(main())
```

| Tool | Use it when | On failure |
|---|---|---|
| `await asyncio.gather(*coroutines)` | Run several, get all results in order | Raises the first exception; the others keep running unless you cancel them |
| `gather(..., return_exceptions=True)` | Partial failure is acceptable | Exceptions are returned in the results list |
| `asyncio.TaskGroup` | All-or-nothing work | Cancels the remaining tasks, raises an `ExceptionGroup` |
| `asyncio.create_task(coro)` | Start something now, await it later | Keep a reference to the task, and await it |

## Timeouts and limits

```python
import asyncio


async def slow_inventory() -> str:
    await asyncio.sleep(5)
    return "assets"


async def limited(semaphore: asyncio.Semaphore, n: int) -> int:
    async with semaphore:  # at most 3 at a time
        await asyncio.sleep(0.05)
        return n


async def main() -> None:
    try:
        async with asyncio.timeout(0.1):  # Python 3.11+
            await slow_inventory()
    except TimeoutError:
        print("inventory timed out: show the dashboard without it")

    semaphore = asyncio.Semaphore(3)
    print(sum(await asyncio.gather(*(limited(semaphore, n) for n in range(10)))))


asyncio.run(main())
```

- A timeout **cancels** the awaited work: the coroutine sees `asyncio.CancelledError` at its current `await`. Don't swallow `CancelledError`.
- A timeout only fires at an `await`. Code that never awaits (a long loop) can't be interrupted.
- A semaphore keeps you inside an API's rate limit, and stops a burst from opening hundreds of connections.

## Calling synchronous code

```python
import asyncio
import time


def blocking_report() -> str:  # a synchronous library call
    time.sleep(0.1)
    return "report"


async def main() -> None:
    # to_thread runs it in a worker thread, so the event loop stays free
    report = await asyncio.to_thread(blocking_report)
    print(report)


asyncio.run(main())
```

## HTTP with HTTPX

```python
import asyncio

import httpx


def handler(
    request: httpx.Request,
) -> httpx.Response:  # a fake server, for this example
    return httpx.Response(200, json={"team": request.url.path.rsplit("/", 1)[-1]})


async def main() -> None:
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport, base_url="https://assets.example.com", timeout=5
    ) as client:
        responses = await asyncio.gather(
            *(client.get(f"/teams/{t}") for t in ("network", "dns"))
        )
    print([r.json()["team"] for r in responses])


asyncio.run(main())
```

Create one `AsyncClient` and share it (in FastAPI, in the lifespan); creating one per request throws away connection reuse.

## Where code runs

| Context | How to run a coroutine |
|---|---|
| A script or CLI | `asyncio.run(main())`, once, at the top |
| A Jupyter notebook | `await main()` directly: the notebook already runs a loop, and `asyncio.run` raises an error there |
| FastAPI | `async def` endpoints run on FastAPI's loop; just `await` |
| pytest | `pytest-asyncio`, and mark each test `@pytest.mark.asyncio` (an unmarked `async def` test fails) |

## Common mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Forgetting `await` | `RuntimeWarning: coroutine '...' was never awaited`, and a coroutine object instead of a result | Add `await` |
| `time.sleep` or `requests` inside `async def` | Everything stalls; "concurrent" code is as slow as sequential | `await asyncio.sleep`, `httpx.AsyncClient`, or `asyncio.to_thread` |
| `asyncio.run` inside a running loop | `RuntimeError: asyncio.run() cannot be called from a running event loop` | `await` instead |
| Using async for CPU-heavy work | No speed-up | A process pool (`concurrent.futures.ProcessPoolExecutor`) |
| Fire-and-forget tasks | Tasks disappear or errors are never seen | Keep a reference and await it, or use a `TaskGroup` |

## Further reading

- [`asyncio`: coroutines and tasks](https://docs.python.org/3.13/library/asyncio-task.html), including `TaskGroup`, `timeout` and `to_thread`.
- [HTTPX: async support](https://www.python-httpx.org/async/).
- [FastAPI: concurrency and `async`/`await`](https://fastapi.tiangolo.com/async/).
