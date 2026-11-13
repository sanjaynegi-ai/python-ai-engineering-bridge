# Python Readiness

This course exists to remove one obstacle: Python itself. This page says what "ready" means at the end of it, what evidence counts, and what to do if you're not there yet.

## What "ready" means

You're ready for further AI engineering study when you can, **on your own and without an AI assistant**:

- create a Python project with `uv`, add dependencies, and get its tests running;
- write correct, readable Python that transforms data with collections, functions and exceptions;
- define a data contract with Pydantic and expose it through a FastAPI service with the right status codes;
- call an LLM API with structured output, handle its failures, and test it without paid calls;
- find and fix bugs from evidence, and write tests that would catch them;
- explain the design decisions in your code, and their trade-offs.

With an assistant, you should be able to do all of that faster, and still explain and defend every line. That's what the capstone shows.

## The evidence

| Evidence | When | What it shows |
|---|---|---|
| **Milestone 1:** Project 01 complete, with tests | After Session 04 | Python fundamentals, packages and pytest |
| **Milestone 2:** Project 02 complete, with tests | After Session 08 | HTTP, Pydantic, FastAPI and asynchronous I/O |
| **Milestone 3:** Project 03 complete, with tests | After Session 12 | Direct LLM integration, LangChain and LangGraph |
| **Milestone 4:** the capstone, presented, and the final assessment | Session 16 | Integration of everything; explanation; independent capability |

Quizzes are formative: they're for you, and they don't count.

## The final assessment

A 60-minute practical in Session 16, without AI assistants: see [`final-assessment.md`](final-assessment.md). Its six tasks follow these weights:

| Competency | Weight |
|---|---:|
| Python fundamentals | 20% |
| Project structure and dependencies | 15% |
| APIs and Pydantic | 20% |
| LLM integration | 20% |
| Testing and debugging | 15% |
| Engineering explanation | 10% |

## The readiness decision

The suggested standard is:

1. **80 or more** out of 100 in the final assessment, **and**
2. the capstone at **"Meets"** or better on every criterion of the [capstone rubric](capstone-rubric.md), **and**
3. Milestones 1 to 3 complete, with their acceptance tests passing.

The 80% threshold is a **proposed** standard. It will be checked against how learners who reach it actually do in later AI engineering programs, and may change. Treat it as a guide to where you stand, not as a verdict.

## If you're not there yet

Find the competency where you lost points, and go back to its sessions. Redo the workbook from a fresh copy of the starter, without looking at your old code, and without an assistant.

| Competency | Revisit |
|---|---|
| Python fundamentals | Sessions 02 and 03: collections, comprehensions, functions, exceptions, dates |
| Project structure and dependencies | Sessions 01 and 04: `uv add`, dependency groups, entry points, the `src/` layout |
| APIs and Pydantic | Sessions 06 and 07: validators, model validators, status codes, `TestClient` |
| LLM integration | Session 09: structured output, provider errors, fakes |
| Testing and debugging | Session 04 and every debugging lab: Observe → Hypothesize → Inspect → Fix → Verify |
| Engineering explanation | The reflection questions at the end of every workbook: answer them in writing |

## Check yourself

Before Session 16, can you do each of these without notes or an assistant, in about ten minutes each?

- [ ] Start a project with `uv init`, add a runtime and a development dependency, and run its tests.
- [ ] Group and sort records by a key, and find runs of consecutive dates.
- [ ] Write a Pydantic model with a field validator and a rule that compares two fields.
- [ ] Write a FastAPI route that returns 201, 404 and 422 in the right cases, and test it.
- [ ] Call `client.responses.parse` with a Pydantic `text_format`, and handle a refusal and an outage.
- [ ] Explain the difference between a naive and an aware `datetime`, and fix code that mixes them.
- [ ] Write a test that fails on a buggy function and passes on a correct one.
