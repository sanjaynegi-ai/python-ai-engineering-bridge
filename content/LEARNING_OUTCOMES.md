# Learning Outcomes

## Course outcomes

By the end of the course, you will be able to:

1. **Read** and explain an unfamiliar Python application: its structure, its dependencies and its control flow.
2. **Create** and maintain reproducible Python projects with `uv`: Python versions, dependencies, lockfiles and dependency groups.
3. **Write** idiomatic, typed and tested Python, organised into packages and modules.
4. **Process** files and JSON, and **integrate** HTTP APIs with timeouts, error handling and secrets kept out of code.
5. **Define** data contracts with Pydantic, and **build** validated APIs with FastAPI.
6. **Use** asynchronous Python for concurrent I/O, and **explain** when it helps and when it doesn't.
7. **Integrate** LLM APIs directly, with structured output, error handling, cost awareness and tests that make no paid calls.
8. **Use** selected LangChain and LangGraph abstractions, and **judge** when plain Python is better.
9. **Build** a simple retrieval-augmented generation application that cites its sources.
10. **Debug** and **test** Python code systematically, and **explain** your design decisions.
11. **Use** AI coding assistants responsibly, reviewing and owning the code they produce.

## Outcomes by session

Each session README lists its full objectives. In short:

| Session | You will be able to |
|---|---|
| 01 | Explain how Python runs code; create a `uv` project with runtime and development dependencies; reproduce it from its lockfile; diagnose a wrong-interpreter problem |
| 02 | Predict reference and mutability behaviour; choose the right collection; write comprehensions and slices; transform nested business records |
| 03 | Design functions with keyword-only arguments and safe defaults; raise, catch and chain exceptions; read tracebacks; process files and JSON safely |
| 04 | Structure a `src/` package; explain and fix import problems; model data with dataclasses; write pytest tests with fixtures and parametrisation; use Ruff and a debugger |
| 05 | Call REST APIs with HTTPX, with timeouts and explicit error handling; load secrets from the environment; design and mock-test an API client |
| 06 | Define Pydantic models with constraints and validators; map validation errors to messages; serialise models; load typed settings |
| 07 | Build a FastAPI service with routers, a service layer, request and response models, and correct status codes; inject and override dependencies; test it with `TestClient` |
| 08 | Explain the event loop; run I/O concurrently with `gather`; apply deadlines; handle partial failure; avoid blocking the loop; test async code |
| 09 | Call an LLM API with structured output validated by Pydantic; handle refusals, truncation and provider errors; calculate cost; test without paid calls; mitigate prompt injection |
| 10 | Rebuild an LLM feature with LangChain, and compare it with the direct SDK on code size, debuggability, testability and lock-in |
| 11 | Load, chunk and embed documents; retrieve by similarity; build grounded prompts with source attribution; diagnose retrieval failures |
| 12 | Build a stateful workflow with LangGraph, with conditional routing; debug it; judge when a graph is worth it |
| 13 | Use an AI coding assistant to explore, plan, implement, test and review a feature, and evaluate the code it produces |
| 14 | Design the capstone; implement repeatable ingestion of PDF and Markdown documents into a vector store |
| 15 | Implement retrieval and grounded generation with sources behind FastAPI and a simple UI; run a small evaluation |
| 16 | Test, debug and explain a complete application, and demonstrate readiness for further AI engineering study |

Sessions 10 to 16 are released over the course; their details may still be refined before release.
