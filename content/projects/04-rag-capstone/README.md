# Project 04: Internal Knowledge Assistant (Capstone)

**Built in:** Sessions 14, 15 and 16 · **Checkpoint:** end of Session 16 (Milestone 4)

## What you build

`knowledge-assistant`, a question-answering assistant for the fictional Orbital Logistics IT operations team. Ask it how to fail over the orders database, or who approves an emergency change, and it answers from the team's runbooks, policies, postmortems and guides, citing the files and pages it used. When the documents don't cover a question, it says so.

| Session | You build | Where |
|---|---|---|
| 14 | Ingestion: find, fingerprint, load, chunk, embed and store the documents in a local Chroma index, doing only the work that changed, surviving broken files and never logging their contents | this project's [`starter/`](starter/README.md) (Session 14 workbook) |
| 15 | Answers: retrieval, a grounded prompt, the LLM's answer with sources, "not found" for unanswerable questions, a FastAPI service, a Streamlit UI and a small evaluation | the same project, plus the files in `session-15/` (Session 15 workbook) |
| 16 | Review: integration tests, structured logging, and a presentation of your design and its limitations | the same project, plus the files in `session-16/` (Session 16 workbook) |

## What it demonstrates

Document ingestion (Markdown and PDF) · chunking with metadata · embeddings · a persistent local vector store · idempotent, incremental processing with content hashes · failure isolation · safe logging · retrieval and grounded generation with source references · FastAPI and Streamlit · retrieval evaluation · module boundaries you can defend · AI-assisted engineering with tests as the specification.

## Getting started

Follow the [Session 14 workbook](../../sessions/session-14/workbook/assignment.md). It has you copy `starter/` into your own folder, design the ingestion pipeline in `ARCHITECTURE.md`, and then build it against the acceptance tests. No test needs an API key or a model download.
<!-- release:8 -->

Then follow the [Session 15 workbook](../../sessions/session-15/workbook/assignment.md), which has you copy [`session-15/`](session-15/) over your project, as earlier projects' add-ons did, and add answers, the API, the UI and the evaluation.

Finally, the [Session 16 workbook](../../sessions/session-16/workbook/assignment.md) completes the capstone with [`session-16/`](session-16/): integration tests, structured logging and your final documentation (Milestone 4). It's assessed with the [capstone rubric](../../assessments/capstone-rubric.md).
<!-- /release:8 -->

All data in this project is synthetic: Orbital Logistics, its systems and its people are invented.
