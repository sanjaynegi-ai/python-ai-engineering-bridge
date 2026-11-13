# Changelog

New material is released weekend by weekend. Each release adds to the previous ones. Run `git pull` at the start of each weekend.

If a file you've already copied into your own work changes, the change is described here; your copy is never changed for you.

<!-- release:8 -->
## Release 8: Weekend 8

- Session 15: RAG capstone, application.
- Project 04 add-on for Session 15: `projects/04-rag-capstone/session-15/`. Copy it over your own project and add three dependencies, as the workbook explains. It replaces four provided files (`errors.py`, `settings.py`, `cli.py`, `tests/conftest.py`); if you changed them, merge your changes back.
- Session 16: Capstone review and Python readiness.
- Project 04 add-on for Session 16: `projects/04-rag-capstone/session-16/`, with integration tests and structured logging. It replaces the provided `cli.py`.
- Assessments: `assessments/python-readiness.md` (the readiness standard), `assessments/capstone-rubric.md`, and `assessments/final-assessment.md` with its project, `assessments/final-assessment/`.
<!-- /release:8 -->
<!-- release:7 -->
## Release 7: Weekend 7

- Session 13: Claude Code for professional engineering.
- Project 03 files for Session 13: `projects/03-llm-application/session-13/`, with acceptance tests for the audit log and an AI-generated pull request to review. The workbook explains how to use them.
- Session 14: RAG capstone, ingestion.
- Project 04 (the capstone) starter: `projects/04-rag-capstone/starter/`, with 24 synthetic documents and the acceptance tests for ingestion. It's a uv project of its own: run `uv sync` in your copy, as the workbook explains.
<!-- /release:7 -->
<!-- release:6 -->
## Release 6: Weekend 6

- Session 11: Retrieval and RAG fundamentals, with a synthetic IT handbook and the `handbook-search` starter in `sessions/session-11/workbook/starter/`.
- The course environment gains a `rag` dependency group (`pypdf`, `chromadb`, `langchain-text-splitters`): run `uv sync`.
- Session 12: Introduction to LangGraph.
- Project 03 add-on for Session 12: `projects/03-llm-application/session-12/`. Copy it into your own Project 03, as the workbook explains. Session 12 completes Project 03 (Milestone 3).
- Reference guide: RAG fundamentals.
<!-- /release:6 -->
<!-- release:5 -->
## Release 5: Weekend 5

- Session 09: Direct LLM API integration.
- Session 10: LangChain fundamentals.
- Project 03 starter: `projects/03-llm-application/starter/`, and its Session 10 add-on: `projects/03-llm-application/session-10/`.
- The course environment gains an `ai` dependency group (LangChain): run `uv sync`.
- Reference guides: LLM API patterns, and LangChain and LangGraph.
<!-- /release:5 -->
<!-- release:4 -->
## Release 4: Weekend 4

- Session 07: FastAPI.
- Session 08: Asynchronous Python.
- Project 02 add-ons for Sessions 07 and 08: `projects/02-python-api-service/session-07/` and `session-08/`. Copy them into your own Project 02, as each workbook explains.
- Reference guides: FastAPI patterns, and async and await.
<!-- /release:4 -->
<!-- release:3 -->
## Release 3: Weekend 3

- Session 05: HTTP and API integration.
- Session 06: Pydantic and data validation.
- Project 01 checkpoint: `projects/01-python-data-processor/checkpoint/`, a complete reference version of Project 01.
- Project 02 starter: `projects/02-python-api-service/starter/`, built from the Project 01 checkpoint.
- Reference guide: Pydantic patterns.
<!-- /release:3 -->
<!-- release:2 -->
## Release 2: Weekend 2

- Session 03: Functions, exceptions, files and JSON.
- Session 04: Modules, packages, classes and testing. Completes Project 01 (Milestone 1).
- Reference guides: Python for QA engineers, and project structure.
<!-- /release:2 -->

## Release 1: Weekend 1

- Session 00: self-study induction to the course roadmap, LLM foundations, model access, RAG and agents.
- Course documents: `README.md`, `COURSE_MAP.md`, `PREREQUISITES.md`, `LEARNING_OUTCOMES.md`.
- The entry diagnostic: `assessments/entry-diagnostic.md`, a 30-minute self-check of the prerequisites.
- Setup and reference guides in `docs/`.
- Reference guides in `reference/`: a Python cheatsheet, a uv cheatsheet, a glossary, and Python for Java, C# and JavaScript developers.
- Session 01: Python runtime and professional setup.
- Session 02: Python language essentials.
- Project 01 starter: `projects/01-python-data-processor/starter/`.
- Validation scripts in `scripts/`.
