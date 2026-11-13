# Final Assessment

**When:** Session 16 · **Time:** 60 minutes · **Type:** **Independent**: no AI coding assistants · **Points:** 100

The final assessment checks that you can do the core of what this course teaches on your own, quickly enough to be useful. It's practical: you finish a small, unfinished Python service, **`swap-desk`**, for on-call week swaps at Orbital Logistics, and explain a few of your decisions in writing.

The project is in [`final-assessment/`](final-assessment/README.md), and its task sheet is [`final-assessment/TASKS.md`](final-assessment/TASKS.md). The Session 16 instructions tell you when to start.

## What it covers

| Task | Competency | Points | What you do |
|---|---|---:|---|
| 1 | Project structure and dependencies | 15 | Get the tests and the command running: dependencies, dependency groups and an entry point |
| 2 | Python fundamentals | 20 | Group, sort and analyse rota data: collections, dates, exceptions |
| 3 | APIs and Pydantic | 20 | A validated request model with cross-field rules, and a small FastAPI service |
| 4 | LLM integration | 20 | A structured-output call with the OpenAI SDK, and the right error handling, tested against a fake |
| 5 | Testing and debugging | 15 | Fix a module with failing tests, and write tests of your own that catch broken code |
| 6 | Engineering explanation | 10 | Four short written answers about your decisions |

## Rules

- Work alone, without AI coding assistants or AI chat tools.
- You may use the official documentation, this course repository, and your own notes and projects.
- Don't change the provided tests.
- Commit when time is up. Unfinished tasks earn partial points.

## How it's scored

- Tasks 1 to 4 count the tests that pass: the provided ones **and further tests of the same written requirements**, which you don't see. Passing every provided test is a good sign, not a guarantee; read the specifications.
- Task 5 counts the fix (tests, as above) and how many incorrect versions of a function your own tests catch.
- Task 6 is marked by hand, for accuracy and reasoning.

The suggested readiness threshold is 80 points, together with the capstone. See [`python-readiness.md`](python-readiness.md) for the full standard, and what to do if you're not there yet.

## How to prepare

- Do the checklist at the end of [`python-readiness.md`](python-readiness.md).
- Make sure `uv` works on your machine, and that your editor's AI features can be switched off.
- Practise reading a specification and writing the code before running the tests: the tests confirm your reading; they don't replace it.
