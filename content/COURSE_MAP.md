# Course Map

Eight weekends, sixteen 2-hour live sessions, four projects. Depth levels say how well you should know each topic by the end:

| Level | Meaning |
|---|---|
| **Awareness** | You recognise it and know why it exists |
| **Working knowledge** | You can use it, with the documentation open |
| **Independent implementation** | You can implement, debug and explain it on your own |
| **Guided integration** | You can combine several technologies into a working application, and explain the design |

## Sessions available now

<!-- sessions:start -->
| Session | Topic |
|---|---|
| [00](sessions/session-00/README.md) | Induction — Python to GenAI Engineering |
| [01](sessions/session-01/README.md) | Python Runtime and Professional Setup |
| [02](sessions/session-02/README.md) | Python Language Essentials |
| [03](sessions/session-03/README.md) | Functions, Exceptions, Files and JSON |
| [04](sessions/session-04/README.md) | Modules, Packages, Classes and Testing |
| [05](sessions/session-05/README.md) | HTTP and API Integration |
| [06](sessions/session-06/README.md) | Pydantic and Data Validation |
| [07](sessions/session-07/README.md) | FastAPI |
| [08](sessions/session-08/README.md) | Asynchronous Python |
| [09](sessions/session-09/README.md) | Direct LLM API Integration |
| [10](sessions/session-10/README.md) | LangChain Fundamentals |
| [11](sessions/session-11/README.md) | Retrieval and RAG Fundamentals |
| [12](sessions/session-12/README.md) | Introduction to LangGraph |
| [13](sessions/session-13/README.md) | Claude Code for Professional Engineering |
| [14](sessions/session-14/README.md) | RAG Capstone, Ingestion |
<!-- sessions:end -->

## The whole course

### Phase 1: Python for experienced developers (Weekends 1–2)

| # | Session | Main topics | Depth | Project work |
|---|---|---|---|---|
| 01 | Python runtime and professional setup | The interpreter and bytecode; virtual environments; `uv` projects, dependencies and lockfiles; VS Code and notebooks | Awareness (runtime); independent (setup) | `ops-toolkit`: a reproducible project |
| 02 | Python language essentials | Dynamic typing and references; lists, tuples, dicts, sets; mutability; comprehensions, slicing, truthiness | Independent | A ticket-summary utility |
| 03 | Functions, exceptions, files and JSON | Arguments and defaults; type hints; exceptions and tracebacks; context managers; `pathlib` and `json` | Independent | An incident-report script |
| 04 | Modules, packages, classes and testing | Imports and packages; the `src/` layout; classes and dataclasses; pytest; Ruff; the debugger | Independent | **Project 01** complete, with tests (**Milestone 1**) |

### Phase 2: Professional Python applications (Weekends 3–4)

| # | Session | Main topics | Depth | Project work |
|---|---|---|---|---|
| 05 | HTTP and API integration | HTTPX; status codes and timeouts; environment variables and secrets; client design; mocked tests | Independent | `asset-lookup`: an API client |
| 06 | Pydantic and data validation | Models and fields; validators; serialisation; `pydantic-settings` | Independent | **Project 02** begins: data contracts |
| 07 | FastAPI | Routes and parameters; request and response models; dependency injection; errors; OpenAPI; `TestClient` | Independent | Project 02: the API service |
| 08 | Asynchronous Python | Coroutines and the event loop; `gather`; timeouts and cancellation; async in FastAPI; the GIL | Working knowledge, with implementation | Project 02 complete (**Milestone 2**) |

### Phase 3: Python for AI applications (Weekends 5–6)

| # | Session | Main topics | Depth | Project work |
|---|---|---|---|---|
| 09 | Direct LLM API integration | The Responses API; structured output with Pydantic; errors and retries; tokens and cost; testing with fakes; prompt injection | Independent | **Project 03** begins: LLM triage |
| 10 | LangChain fundamentals | Why frameworks exist; models, prompts and runnables; structured output; comparing with the direct SDK | Guided integration | Project 03 with LangChain |
| 11 | Retrieval and RAG fundamentals | Loading and chunking documents; embeddings; a vector store; grounded answers with sources | Guided integration | A retrieval pipeline |
| 12 | Introduction to LangGraph | When a graph helps; state, nodes and edges; conditional routing; debugging | Working knowledge and guided integration | Project 03 complete (**Milestone 3**) |

### Phase 4: AI-assisted engineering and the RAG capstone (Weekends 7–8)

| # | Session | Main topics | Depth | Project work |
|---|---|---|---|---|
| 13 | Claude Code for professional engineering | Exploring a codebase; planning; writing requests; testing and reviewing generated code; security | Practical workflow | An AI-assisted feature, reviewed |
| 14 | RAG capstone: ingestion | Capstone architecture; PDF and Markdown ingestion; metadata; embeddings; repeated ingestion | Guided integration | **Project 04**: ingestion |
| 15 | RAG capstone: application | Retrieval and context; generation with sources; FastAPI and Streamlit; basic evaluation | Guided integration | Project 04: the application |
| 16 | Capstone review and Python readiness | Integration testing; logging; architecture decisions; demonstration; practical assessment | Assessment | Project 04 complete (**Milestone 4**) |

## Projects

| Project | Sessions | What you build |
|---|---|---|
| 01: Python Data Processor | 02–04 | A command-line report over incident ticket exports: validation, SLA breaches, per-team metrics; a tested package |
| 02: Python API Service | 05–08 | The same domain as a FastAPI service: Pydantic contracts, endpoints, and a concurrent dashboard calling another API |
| 03: LLM-Powered Application | 09–12 | LLM-assisted triage of free-text reports: direct SDK, then LangChain, then a LangGraph workflow |
| 04: Internal Knowledge Assistant | 14–16 | Retrieval-augmented question answering over synthetic company documentation, with sources, an API and a UI |

## Independent work

Plan for 3 to 5 hours between weekends, roughly half for each session: revise the concepts notebook, answer the quiz, then do the workbook. The workbooks are the most important part. They're where you write code on your own, and the projects build on them.
