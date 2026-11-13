# Project 03: LLM-Powered Application

**Built in:** Sessions 09, 10 and 12 · **Checkpoint:** end of Session 12 (Milestone 3)

## What you build

`incident-triage`, a tool for the fictional Orbital Logistics on-call team. It reads free-text incident reports and returns a structured, validated triage for each: priority, owning team, category, affected system, a one-line summary and tags.

| Session | You build | Where |
|---|---|---|
| 09 | Direct integration with OpenAI's Responses API: structured output, validation, typed errors, token usage and cost, and tests with HTTP-level fakes | this project's [`starter/`](starter/README.md) (Session 09 workbook) |
| 10 | The same triage with LangChain, proven equivalent by shared tests, and a measured comparison | the same project, plus the files in `session-10/` (Session 10 workbook) |
| 12 | A routing workflow (page, queue or review, with retries and a fallback), in plain Python and as a LangGraph graph, proven equivalent and compared | the same project, plus the files in `session-12/` (Session 12 workbook) |

## What it demonstrates

Direct LLM API integration · structured outputs · Pydantic validation of model output · error handling and retries · configuration and secrets · token usage and cost · interfaces and fakes for testing · prompt-injection awareness · framework trade-offs (LangChain, LangGraph) · workflows with routing, fallbacks and loop limits · contract tests across implementations.

## Getting started

Follow the [Session 09 workbook](../../sessions/session-09/workbook/assignment.md), then the [Session 10 workbook](../../sessions/session-10/workbook/assignment.md), which has you copy [`session-10/`](session-10/) over your project. No test needs an API key, and the `--offline` mode runs the whole tool without one.
<!-- release:6 -->

Then follow the [Session 12 workbook](../../sessions/session-12/workbook/assignment.md), which has you copy [`session-12/`](session-12/) over your project in the same way. Project 03 is complete at the end of Session 12 (Milestone 3).
<!-- /release:6 -->
<!-- release:7 -->

Session 13 returns to the project with an AI coding assistant: the [Session 13 workbook](../../sessions/session-13/workbook/assignment.md) adds an audit log (acceptance tests in [`session-13/tests/`](session-13/tests/)) and has you review an AI-generated pull request (in [`session-13/review/`](session-13/review/)).
<!-- /release:7 -->

All data in this project is synthetic.
