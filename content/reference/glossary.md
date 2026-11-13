# Glossary

Terms the course uses, grouped by the sessions that teach them, alphabetical within each group. Definitions are short on purpose: follow the session link for the explanation.

## Python and its tools (Sessions 01 and 02)

- **Bytecode:** the instructions CPython compiles your source into before running it, cached in `__pycache__/`. Compilation checks syntax, not types.
- **Comprehension:** an expression that builds a list, dict or set from an iterable: `[t["id"] for t in tickets if t["open"]]`.
- **CPython:** the standard Python interpreter, the one uv installs.
- **Dependency group:** a named set of dependencies in `pyproject.toml`, such as `dev` for tools that tests need but users don't.
- **Dictionary (`dict`):** a mapping from keys to values, keeping insertion order.
- **f-string:** a string literal with `{expressions}` evaluated inline: `f"{team}: {count}"`.
- **Immutable:** can't be changed after creation: `int`, `str`, `tuple`, `frozenset`. Changing it means making a new object.
- **Interpreter:** the program that runs Python code. `uv run python` uses the project's interpreter.
- **Iterable:** anything a `for` loop can walk through: lists, dicts, files, generators.
- **Jupyter kernel:** the Python process that runs a notebook's cells. It must be the course environment's interpreter.
- **Lockfile (`uv.lock`):** the exact version of every package, so every machine installs the same set.
- **Mutable:** can be changed in place: `list`, `dict`, `set`, most objects.
- **`None`:** Python's single "no value" object. Test it with `is None`.
- **`pyproject.toml`:** a project's declaration: name, Python version, dependencies, entry points, tool settings.
- **Reference:** a name points to an object; assigning or passing it shares the object rather than copying it.
- **Slicing:** taking part of a sequence: `items[1:3]`, `text[::-1]`.
- **Truthiness:** how values behave in `if`: `None`, `0`, `""` and empty collections are false.
- **Tuple:** an immutable, ordered group of values: `("P1", 4)`.
- **uv:** the course's tool for Python versions, project environments and dependencies.
- **Virtual environment (`.venv`):** a project's private set of installed packages, built from the lockfile.
<!-- release:2 -->

## Functions, packages and tests (Sessions 03 and 04)

- **Context manager:** an object used with `with`, which guarantees cleanup: `with open(path) as file:`.
- **`dataclass`:** a decorator that writes `__init__`, `__eq__` and `__repr__` from annotated fields.
- **Default argument:** a parameter's value when the caller omits it. Evaluated once, so never use a mutable default.
- **Entry point (console script):** a command, declared in `[project.scripts]`, that runs a function: `incident-report = "incident_report.cli:main"`.
- **Exception chaining:** `raise NewError(...) from error`, which keeps the original cause in the traceback.
- **Fixture:** a pytest function that provides test data or resources, requested by naming it as a test parameter.
- **Keyword-only argument:** a parameter after `*` in a signature, which callers must pass by name.
- **Module:** one `.py` file; its top-level names can be imported.
- **Package:** a folder of modules with an `__init__.py`.
- **Parametrize:** running one test with several inputs: `@pytest.mark.parametrize`.
- **Property:** a method accessed like an attribute, with `@property`.
- **Protocol:** a type that describes required methods and attributes; any class with that shape matches, without declaring it.
- **pytest:** Python's de facto test runner: plain `assert` in functions named `test_*`.
- **Ruff:** the course's linter (`ruff check`) and formatter (`ruff format`).
- **Scope:** where a name is visible: local to a function, global to a module, or built in.
- **`src` layout:** keeping the package under `src/`, so tests import the installed package rather than a stray copy.
- **Traceback:** the report of an exception: the call stack, **most recent call last**, then the error.
- **Type hint:** an annotation such as `count: int`. Documentation and tooling only: Python doesn't enforce it at run time.
<!-- /release:2 -->
<!-- release:3 -->

## HTTP and validation (Sessions 05 and 06)

- **Environment variable:** a named value from the operating system, used for configuration and secrets.
- **Fake (test double):** a simple stand-in for a real dependency, used in tests.
- **HTTPX:** the course's HTTP client library, with sync and async clients.
- **Idempotent:** having the same effect however many times it runs. `GET`, `PUT` and `DELETE` should be; `POST` usually isn't.
- **Pydantic:** the library that validates data into typed models and serialises them back.
- **pydantic-settings:** Pydantic models that read their values from environment variables and `.env`.
- **respx:** a library that intercepts HTTPX requests in tests.
- **Retry with backoff:** repeating a failed call after increasing delays, only for errors that may be temporary.
- **Secret:** a key, token or password. Kept in `.env` or a secret manager; never in code, Git or logs.
- **Serialisation:** turning objects into a format such as JSON (`model_dump_json`), and back (`model_validate_json`).
- **Status code:** the number an HTTP response starts with: 2xx success, 4xx the client's fault, 5xx the server's.
- **Timeout:** the longest you'll wait for a response before treating the call as failed.
- **Validator:** a function attached to a Pydantic model that checks or transforms a field (`@field_validator`) or the whole model (`@model_validator`).
<!-- /release:3 -->
<!-- release:4 -->

## Services and concurrency (Sessions 07 and 08)

- **`asyncio`:** the standard library's framework for coroutines and the event loop.
- **Blocking call:** a call that holds the thread while it waits (`time.sleep`, a sync HTTP request). Fatal inside `async def`.
- **Coroutine:** what an `async def` function returns; it runs when awaited or scheduled as a task.
- **Dependency injection (`Depends`):** FastAPI providing a route's collaborators (a service, settings), replaceable in tests.
- **Event loop:** the scheduler that runs coroutines on one thread, switching between them at each `await`.
- **FastAPI:** the course's web framework: typed functions become HTTP endpoints.
- **`gather`:** `asyncio.gather(...)` runs several coroutines concurrently and returns their results in order.
- **GIL (global interpreter lock):** lets only one thread run Python code at a time in CPython, so threads help with I/O, not CPU work.
- **Lifespan:** a FastAPI function that sets up shared resources at startup and releases them at shutdown.
- **OpenAPI:** the machine-readable API description FastAPI generates, shown at `/docs`.
- **Path and query parameters:** values from the URL path (`/tickets/{id}`) and from the query string (`?team=dns`).
- **Request and response models:** Pydantic models for a route's input and output, which FastAPI validates and documents.
- **`TaskGroup`:** runs tasks together, and cancels the rest if one fails.
- **`TestClient`:** calls a FastAPI application in-process from tests, with no server.
<!-- /release:4 -->
<!-- release:5 -->

## LLM applications (Sessions 09 and 10)

- **Context window:** the most tokens a model can take in one request, input and output together.
- **Instructions:** the part of a request that carries your rules, kept separate from untrusted input.
- **LangChain:** a framework of common interfaces over models, prompts and parsers, composed into chains.
- **LCEL:** LangChain's `|` syntax for composing runnables: `prompt | model | parser`.
- **LLM (large language model):** a model that generates text from text, called through a provider's API.
- **Prompt injection:** text in the input (a report, a document, a web page) that tries to change the model's behaviour.
- **Provider:** the company or service running the model: OpenAI, Anthropic, OpenRouter, or a local Ollama.
- **Refusal:** the model declining to answer. With structured output, `output_parsed` is `None`.
- **Runnable:** any LangChain component with `invoke`, `batch` and `stream`.
- **SDK:** a provider's client library, such as `openai`.
- **Structured output:** the model's reply constrained to a JSON schema, validated into a Pydantic model.
- **Token:** the unit models read and write, and are billed by: roughly three-quarters of an English word.
<!-- /release:5 -->
<!-- release:6 -->

## Retrieval and workflows (Sessions 11 and 12)

- **Chroma:** the local vector database the course uses.
- **Chunk:** a passage of a document, the unit that's embedded, retrieved and cited.
- **Citation:** a reference in an answer, such as `[2]`, to the source it came from.
- **Conditional edge:** a LangGraph edge whose destination a function chooses from the state.
- **Cosine similarity:** how closely two vectors point the same way, from -1 to 1; for normalised vectors, their dot product.
- **Embedding:** a vector that represents a text's meaning, so similar texts have nearby vectors.
- **Grounding:** making an answer depend only on retrieved sources, with citations.
- **Hit rate:** the share of answerable questions for which an expected document was retrieved.
- **LangGraph:** a library for stateful workflows as graphs of nodes and edges.
- **Node:** a step in a LangGraph graph: a function that reads the state and returns updates.
- **Overlap:** text repeated at the end of one chunk and the start of the next, so an answer isn't cut in half.
- **RAG (retrieval-augmented generation):** retrieve relevant passages, then generate an answer from them.
- **Recursion limit:** the most steps a LangGraph run may take before it stops with an error.
- **State:** the shared data a graph's nodes read and update.
- **Vector store:** a database that stores vectors with their text and metadata, and finds the nearest ones.
<!-- /release:6 -->
<!-- release:7 -->

## AI-assisted engineering and ingestion (Sessions 13 and 14)

- **AI coding assistant:** a tool such as Claude Code that reads, plans, edits and runs code with you.
- **`CLAUDE.md` / `AGENTS.md`:** project instruction files that assistants read at the start of a session.
- **Content hash:** a fingerprint of a file's bytes (SHA-256) that changes when, and only when, its content does.
- **Idempotent ingestion:** ingestion you can run again safely: unchanged files are skipped, changed ones replaced, deleted ones removed.
- **Permission mode:** how much an assistant may do without asking: read only, edit, or run commands.
- **Plan mode:** an assistant mode that explores and proposes changes without making them.
- **Stable ID:** an identifier derived from what it identifies (`source#index`), so writing it again replaces rather than duplicates.
<!-- /release:7 -->
<!-- release:8 -->

## The application and readiness (Sessions 15 and 16)

- **Adapter:** a thin layer (an API, a UI, a CLI) that translates its world into calls on one service.
- **Context variable (`contextvars`):** a variable with a separate value per task or request, used for request IDs.
- **Evaluation set:** questions with known answers, including unanswerable ones, used to measure the assistant.
- **Integration test:** a test that wires real modules together, faking only external services.
- **Percentile (p95):** the value 95% of measurements are at or below. Used for latency, because averages hide the slow tail.
- **Rejection rate:** the share of unanswerable questions the assistant correctly declines.
- **Request ID:** an identifier attached to every log line one request produces.
- **Streamlit:** a library for small web UIs written as Python scripts that rerun on every interaction.
- **Structured logging:** log lines with named fields (usually JSON), not sentences, so they can be queried.
- **Threshold (`min_score`):** the lowest similarity a chunk needs to count as found. It belongs to one embedding model.
<!-- /release:8 -->
