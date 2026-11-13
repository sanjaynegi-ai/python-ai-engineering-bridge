# Session 16: Capstone Review and Python Readiness

**Phase 4: AI-Assisted Engineering and RAG Capstone** · Weekend 8 · 2-hour live session

## 1. Session overview

The last session is about evidence. You take the **final readiness assessment**: 60 minutes, without AI assistants, finishing a small Python service that touches every core skill of the course. Then you **demonstrate your capstone** in five minutes and answer questions about its design.

After the session, you complete the capstone (**Milestone 4**): integration tests that wire the whole assistant together, structured JSON logs with request IDs, a small log report, and final documentation. The concepts notebook covers all of that, using examples that leave the capstone code to you.

## 2. Why this matters

An application that passes its module tests can still fail where modules meet, or over time, when documents change and caches don't. A service whose logs are sentences can't tell you, during an incident, how many answers were "not found" or which request was slow. And an engineer who can only work with an assistant beside them can't judge what the assistant writes.

This session checks all three: the system as a whole, your ability to operate and explain it, and your Python on your own. Those are what the next stage of AI engineering study assumes.

## 3. Prerequisites

**Knowledge:** the whole course; especially Session 04 (testing), Sessions 06–07 (Pydantic, FastAPI), Session 09 (LLM integration), and Sessions 14–15 (the capstone).

**Setup:**

- Your `knowledge-assistant`, tagged `session-15`, with all 136 tests passing.
- `PRESENTATION.md` prepared (workbook Part A).
- For the assessment: `uv` working, and your editor's AI features switched off.

## 4. Learning objectives

By the end of this session you will be able to:

1. **Run** integration tests across a complete application, and **debug** their failures under time pressure.
2. **Implement** structured logging with request IDs, and **explain** what you would observe in production.
3. **Present** your architecture, and **defend** its design decisions and known limitations.
4. **Complete** the practical readiness assessment independently.

## 5. Estimated time

| Activity | Time |
|---|---:|
| Live session (assessment and demonstrations) | 2 hours |
| Workbook Part A (before) | 30 minutes |
| Concepts notebook (revision) | 40 minutes |
| Practice quiz | 30 minutes |
| Workbook Part C (after): Milestone 4 | about 3 hours |

## 6. Concepts covered

| Concept | Depth |
|---|---|
| Unit, acceptance and integration tests: what each catches | Independent implementation |
| Time-boxed debugging | Independent implementation |
| Structured logging: formatters, `extra=` fields, JSON lines | Independent implementation |
| Request IDs with `contextvars` and FastAPI middleware | Working knowledge |
| Operational questions from logs: percentiles, rates, tokens | Guided integration |
| Presenting and defending an architecture | Practical |
| Readiness and next steps | Awareness |

### Live session plan

| Time | Activity |
|---|---|
| 0:00–0:10 | **Briefing.** The assessment's rules and scoring; switching off AI features; copying the project |
| 0:10–1:10 | **Final assessment** (60 minutes, Independent) |
| 1:10–1:40 | **Capstone demonstrations**, in small groups: five minutes each, then questions |
| 1:40–2:00 | **Recap.** Milestone 4 (workbook Part C), the readiness standard, and what to learn next |

## 7. Live demonstration

There's no instructor demonstration this time: **the demonstrations are yours**. Each one follows the structure in notebook Part 5 and is assessed against the [capstone rubric](../../assessments/capstone-rubric.md): the problem, your architecture, two decisions with their alternatives, a live answer and a live "not found", and your limitations.

## 8. Guided exercises

- **Notebook Part 1:** two components that each pass their tests, and fail together. Which test would have caught it?
- **Notebook Part 2:** the stale-cache bug, worked through Observe → Hypothesize → Inspect → Fix → Verify with time boxes.
- **Notebook Part 4:** answer an on-call engineer's questions from a synthetic day of logs.
- **Quiz Q3:** the not-found rate jumped after a deployment. Where do you look first?

## 9. Independent assignment

[`workbook/assignment.md`](workbook/assignment.md): **Capstone completion.** Before the session, prepare your demonstration (Independent). In the session, the final assessment (Independent). After it, complete Milestone 4 (AI-assisted): the logging setup, the integration tests and one of your own, events with request IDs, a log report, and final documentation, against 22 new tests.

## 10. Expected deliverables

- **In the session:** your final-assessment repository, committed when time is up; your demonstration.
- **After the session:** your `knowledge-assistant` tagged `session-16`, with all 158 tests and your own passing, `scripts/log_report.py`, and current `ARCHITECTURE.md`, `EVALUATION.md`, `PRESENTATION.md` and `README.md`.

## 11. Common mistakes

| Mistake | Consequence | Better |
|---|---|---|
| Trusting module tests alone | Parts that disagree, or caches that go stale, reach users | Integration tests that change data and ask again |
| Fixing before reproducing | You can't tell when you're done | Write the failing test first, under time pressure too |
| Log messages built from data | Hard to query, and they leak questions | A constant message, facts in fields, no text fields |
| A request ID passed through every function | Intrusive, and easy to forget | `contextvars`, set once by middleware |
| Averages for latency | The slow tail is hidden | Percentiles: p50 and p95 |
| A demonstration that tours features | No time left for decisions and limitations | Problem, architecture, decisions, evidence, limitations |
| Relying on the provided tests in the assessment | Hidden tests of the same requirements fail | Read the specification; the tests confirm it |

## 12. Reading resources

[`resources/references.md`](resources/references.md): the Logging HOWTO and Cookbook, `contextvars`, FastAPI middleware, pytest's `caplog`, and the course's assessment documents.

## 13. Reflection questions

1. Which bug in the capstone taught you the most, and which kind of test caught it?
2. What can your logs tell an on-call engineer, and what can't they?
3. In the assessment, which task took longer than you expected, and why?
4. Which decision in your capstone would you make differently now?
5. Which Python habit changed most since Session 01?

## 14. Interview questions

1. "Walk me through the architecture of something you built, and one decision you'd change."
2. "What's the difference between a unit test, an integration test and an end-to-end test? Give an example of a bug only an integration test would catch."
3. "How would you trace one user's request through your service's logs?"
4. "What would you alert on for a RAG service in production?"
5. "Your service is slow for some users. How do you find out who, and why?"
6. "How do you use AI coding assistants, and how do you make sure their code is right?"

## 15. Next-session preparation

This is the last session. After it:

- Complete Milestone 4 (workbook Part C) and tag `session-16`.
- Read [`assessments/python-readiness.md`](../../assessments/python-readiness.md): what your assessment result means, and what to revisit if a competency was weak.
- Keep your capstone. It's a portfolio piece: a tested, documented, observable RAG application that you can explain line by line.
