# Session 08: Asynchronous Python

**Phase 2: Professional Python Applications** · **Project 02 completes (Milestone 2)**

## Session overview

AI applications spend most of their time **waiting**: for an LLM, a vector store, another team's API. This session shows how Python waits for many things at once with `async` and `await`. You'll learn the event loop as a mental model, run coroutines concurrently, put deadlines on them, and decide what happens when some of them fail. You'll also learn when async doesn't help: CPU-bound work, and code that blocks.

The workbook finishes Project 02: an on-call dashboard that fetches every team's assets from the Asset Inventory **concurrently**, through one shared async client, with a deadline per team, and still answers when the inventory is down.

## Why this matters

From Session 09 on, nearly every interesting call you make takes seconds: LLM completions, embeddings, retrieval. Making those calls one after another is the most common reason AI prototypes feel slow. Async lets one process keep many of them in flight. The LLM SDKs you'll use offer async clients, and FastAPI runs on an event loop.

Async also has sharp edges that experienced developers from other languages trip over. In Python, a coroutine you forget to `await` silently never runs, and a single blocking call stalls every request to your service. Knowing these failure modes is part of the job.

## Prerequisites

**Knowledge:** Sessions 01–07. In particular, Session 05's HTTP client, and Session 07's dependencies and lifespan.

**Before the session:**

1. In the course repository, run `uv sync`. It adds pytest-asyncio to the notebook kernel.
2. Finish the Session 07 workbook and tag it `session-07`.
3. Have your Session 05 `asset-lookup` project at hand. You'll port its client.

## Learning objectives

By the end of this session you will be able to:

1. **Explain** the event loop, and **decide** whether async will help a given workload (I/O-bound or CPU-bound, and the role of the GIL).
2. **Write** coroutines with `async def` and `await`, and **run** them concurrently with `asyncio.gather`, `TaskGroup` and a `Semaphore`.
3. **Convert** a synchronous HTTP client into one built on `httpx.AsyncClient`, shared across an application.
4. **Apply** deadlines with `asyncio.timeout`, and **handle** cancellation and partial failure deliberately.
5. **Identify** and **fix** common async mistakes: a missing `await`, blocking calls in coroutines, `asyncio.run` inside a running loop, races across an `await`.
6. **Choose** between `def` and `async def` FastAPI endpoints.
7. **Test** async code with pytest-asyncio, proving concurrency without timing assertions.


## Concepts covered

| Concept | Depth |
|---|---|
| Coroutines, `async def`, `await`, `asyncio.run` | Independent implementation |
| The event loop; I/O-bound versus CPU-bound work | Working knowledge |
| `asyncio.gather`, `create_task` | Independent implementation |
| `httpx.AsyncClient`, one shared client | Independent implementation |
| `asyncio.timeout`, cancellation, `CancelledError` | Independent implementation |
| Partial failure: per-item handling, `return_exceptions`, `TaskGroup` and `except*` | Working knowledge |
| `asyncio.Semaphore` to limit concurrency | Working knowledge |
| `def` versus `async def` in FastAPI; `asyncio.to_thread` | Independent implementation |
| The GIL, threads and processes for CPU work | Awareness |
| pytest-asyncio; fakes that count requests in flight | Independent implementation |



## Guided exercises

1. [`notebooks/01-concepts.ipynb`](notebooks/01-concepts.ipynb):
   - **Coroutines:** lazy coroutine objects; a comparison with JavaScript and C#.
   - **The event loop:** sequential versus `gather`; tasks.
   - **Concurrent HTTP:** `httpx.AsyncClient`, peak requests in flight, and a semaphore.
   - **Timeouts and cancellation:** `asyncio.timeout` and HTTPX timeouts.
   - **Partial failure:** `gather`, `return_exceptions`, `TaskGroup`, and per-item handling.
   - **FastAPI:** blocking and non-blocking endpoints under load.
   - **CPU-bound work:** why async doesn't help, and what does.
   - **Testing:** pytest-asyncio on a small project.
2. [`notebooks/03-async-debugging-lab.ipynb`](notebooks/03-async-debugging-lab.ipynb): six broken async programs to diagnose and fix.
3. [`notebooks/02-practice-quiz.ipynb`](notebooks/02-practice-quiz.ipynb): 10 self-check questions.

## Independent assignment

[**Workbook: the on-call dashboard, concurrently**](workbook/assignment.md) (*Independent*: no AI coding assistant)

Port your Session 05 client to `httpx.AsyncClient`, fetch every team's assets concurrently with a deadline per team, turn inventory failures into per-team errors, and serve the result from an `async def` endpoint using one client shared through the lifespan. Then measure it against a fake inventory with real latency. 48 new acceptance tests are provided, one file per milestone, and you write at least 8 async tests of your own. This completes Project 02. The new files are in [`projects/02-python-api-service/session-08`](../../projects/02-python-api-service/README.md).

## Expected deliverables

- The `incident-api` project with `inventory.py`, `dashboard.py` and `GET /dashboard`, tagged `session-08` and `project-02`.
- `uv run pytest` passing: 164 acceptance tests, unchanged, plus your own.
- `NOTES.md` with your predictions, measurements and reflection; an updated `README.md` for the finished service.

## Common mistakes

| Mistake | Instead |
|---|---|
| Calling a coroutine without `await` | `await` it, or pass it to `gather` / a `TaskGroup` |
| `time.sleep`, `requests` or sync `httpx` inside `async def` | Async libraries, `asyncio.to_thread`, or a plain `def` endpoint |
| `asyncio.run()` inside a running loop | `await` directly; `asyncio.run` only at a program's entry point |
| Awaiting independent calls one by one | `asyncio.gather` or a `TaskGroup` |
| A new `AsyncClient` per call | One shared client, created and closed by the lifespan |
| No deadline on external calls | HTTPX timeouts plus `asyncio.timeout` |
| One deadline around everything when results are independent | A deadline per item |
| `except Exception` to "handle" partial failure | Catch the external failures you expect; let bugs propagate |
| Expecting async to speed up CPU work | Processes, native libraries, or another service |
| Read-modify-write across an `await` | Update in one step, or use an `asyncio.Lock` |

## Reading resources

Curated official documentation for this session: [`resources/references.md`](resources/references.md).

## Reflection questions

1. Where in your current (non-Python) systems is time spent waiting on I/O, and how is that handled today?
2. What did the per-team deadline and per-team errors cost in code, and what did they buy the on-call engineer?
3. Which async mistake from the lab would be hardest to notice in production, and how would you detect it?
4. When would you choose threads over async in Python? When processes?

## Interview questions

Practise answering these out loud and support each answer with clear engineering reasoning:

1. Explain how the asyncio event loop works, without code.
2. What happens if you call an `async def` function without `await`? How is that different in JavaScript?
3. When does async make a Python program faster, and when doesn't it? Where does the GIL fit in?
4. How do you put a timeout on several awaited calls, and how does cancellation work?
5. One of ten concurrent calls fails. What are your options, and how do you choose?
6. Should a FastAPI endpoint be `def` or `async def`? What goes wrong if you choose badly?
7. How do you test that code really runs concurrently?

## Next-session preparation

**Session 09: Direct LLM API Integration** starts Phase 3. You'll call an LLM provider's SDK directly from Python, get structured output validated with Pydantic, and test it without paid calls.

Before the session:

- Finish this workbook and tag `session-08` and `project-02`.
- **Set up an LLM API key**, as in Session 01 Part 8, and keep it out of Git (`.env`, never committed). It's optional: everything in Session 09 also runs without one. The default provider is OpenAI; Session 01 Part 8 showed the alternatives.
- Revisit Session 06's `ValidationError` handling: Session 09 applies it to LLM output.

---

<!-- skillup-branding:start -->
## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center">
  <img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="#SkillUpWithSanjay logo" width="60">
</p>

<p align="center">
  <strong>#SkillUpWithSanjay</strong><br>
  <a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>
  &nbsp;&middot;&nbsp;
  <a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
</p>
<!-- skillup-branding:end -->
