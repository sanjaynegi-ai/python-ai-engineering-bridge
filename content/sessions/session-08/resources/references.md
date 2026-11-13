# Session 08: References

Official documentation first. Each link says *why* it's worth your time, so you can pick what you need instead of reading everything.

## Python's `asyncio`

| Resource | Read it for |
|---|---|
| [Coroutines and tasks](https://docs.python.org/3.13/library/asyncio-task.html) | `async def`, `await`, `create_task`, `gather`, `TaskGroup`, `timeout` and cancellation: the core of this session |
| [Runners](https://docs.python.org/3.13/library/asyncio-runner.html) | `asyncio.run`, and why there's only one event loop per thread |
| [Synchronization primitives](https://docs.python.org/3.13/library/asyncio-sync.html) | `Semaphore` and `Lock` |
| [Developing with asyncio](https://docs.python.org/3.13/library/asyncio-dev.html) | Debug mode, "never awaited" warnings, and detecting blocking calls |
| [Exception groups and `except*`](https://docs.python.org/3.13/tutorial/errors.html#raising-and-handling-multiple-unrelated-exceptions) | What a `TaskGroup` raises, and how to handle it |
| [Global interpreter lock (glossary)](https://docs.python.org/3.13/glossary.html#term-global-interpreter-lock) | What the GIL is, in one paragraph |
| [`concurrent.futures`](https://docs.python.org/3.13/library/concurrent.futures.html) | Thread and process pools, for blocking and CPU-bound work |

## Libraries

| Resource | Read it for |
|---|---|
| [HTTPX: async support](https://www.python-httpx.org/async/) | `AsyncClient`, and using one client for many requests |
| [HTTPX: timeouts](https://www.python-httpx.org/advanced/timeouts/) | The four HTTP timeout phases, as opposed to `asyncio.timeout` |
| [FastAPI: concurrency and async / await](https://fastapi.tiangolo.com/async/) | When to write `def` or `async def` endpoints, with a memorable analogy |
| [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/stable/) | Marking async tests, strict and auto modes, async fixtures |

## Background

| Resource | Read it for |
|---|---|
| [PEP 492: coroutines with async and await syntax](https://peps.python.org/pep-0492/) | Why Python's coroutines work the way they do |
| [PEP 703: making the GIL optional](https://peps.python.org/pep-0703/) | The free-threaded build, and where Python is heading |
