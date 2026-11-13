# Session 10: LangChain Fundamentals

**Phase 3: Python for AI Applications** · Weekend 5 · 2-hour live session · **Project 03, stage 2**

## 1. Session overview

In Session 09 you called an LLM directly with the provider's SDK. This session rebuilds the same triage with **LangChain**, the most widely used Python framework for LLM applications: chat models, messages, prompt templates, runnables composed with `|`, and structured output. Then it asks the engineering question properly: what does the framework give you, what does it hide, and when is it worth it?

The workbook adds a `LangChainTriager` to Project 03, behind the same interface as your direct version, proves with shared tests that both behave identically, and ends with a measured comparison and a recommendation.

## 2. Why this matters

You'll meet LangChain in AI codebases, tutorials and job descriptions, and the RAG and workflow tools in Sessions 11 and 12 build on it. You need to read it, use it, and debug it.

You also need to judge it. Experienced engineers are expected to say when a framework helps and when it's an unnecessary layer, with evidence. Having written the direct version first, you can see exactly what LangChain adds, and where its abstractions leak.

## 3. Prerequisites

**Knowledge:** Sessions 01–09. In particular, Session 09's `Triager` interface, error table and test fakes, and Session 08's concurrency and partial failure.

**Before the session:**

1. In the course repository, run `git pull` and `uv sync`. It adds LangChain to the notebook kernel (the `ai` group).
2. Finish the Session 09 workbook and tag it `session-09`.
3. Write down, in a few lines, what you'd want a framework to do for you, having written the direct version.

## 4. Learning objectives

By the end of this session you will be able to:

1. **Explain** LangChain's package structure, and what it abstracts compared with a provider SDK.
2. **Use** chat models, messages and prompt templates, keeping untrusted text out of system messages.
3. **Compose** runnables with `|`, and **run** them with `invoke` and `batch`.
4. **Implement** structured output with `with_structured_output`, and **handle** each way it fails.
5. **Apply** retries and fallbacks without multiplying requests or hiding outages.
6. **Switch** provider through configuration, and **identify** the differences that remain.
7. **Compare** a framework implementation with a direct one on measurable criteria, and **recommend** one.

## 5. Estimated time

| Activity | Time |
|---|---:|
| Live session | 2 hours |
| Concepts notebook (revision on your own) | 60 minutes |
| Practice quiz | 35 minutes |
| Workbook assignment (Project 03, stage 2) | 2–2.5 hours |

## 6. Concepts covered

| Concept | Depth |
|---|---|
| LangChain packages: core, integrations, `langchain`, LangGraph, LangSmith | Working knowledge |
| Chat models and messages; `usage_metadata` | Guided integration |
| `ChatPromptTemplate` and variables | Guided integration |
| Runnables and LCEL: `|`, `invoke`, `batch`, `RunnableLambda` | Guided integration |
| `with_structured_output` and `include_raw` | Guided integration |
| Provider-neutral exceptions, and their gaps | Guided integration |
| `with_retry`, `with_fallbacks` | Working knowledge |
| `init_chat_model` and switching provider | Working knowledge |
| Callbacks; LangSmith tracing | Awareness |
| Choosing between a framework and a direct SDK | Independent judgment |

### Live session plan

| Segment | Time | What happens |
|---|---:|---|
| Problem and intuition | 20 min | "Why didn't you use LangChain?" The packages, and the two-column picture |
| Visual explanation and demo | 25 min | Model, prompt, `|`, `batch`; structured output and how each failure surfaces |
| Guided coding | 40 min | Together: `PROMPT` and `LangChainTriager.from_settings`, until the request tests pass for both implementations |
| Debugging challenge | 20 min | A `408` that escapes the abstraction, 9 requests from double retries, and a template that invites injection |
| Recap and assignment briefing | 15 min | Key takeaways; the comparison criteria |

## 7. Live demonstration

The instructor will:

1. Call a chat model with messages, and read `usage_metadata`.
2. Build a prompt template, then a `prompt | model | parser` chain, and batch it.
3. Get a `TriageResult` with `include_raw=True`, then feed it a refusal, truncated output and a rule-breaking summary.
4. Show which HTTP failures LangChain's exceptions cover, and which they don't.
5. Stack `with_retry` on the SDK's retries, and count the requests.
6. Swap the model for Anthropic with `init_chat_model`, keeping the chain unchanged.

## 8. Guided exercises

1. [`notebooks/01-concepts.ipynb`](notebooks/01-concepts.ipynb) (free by default; live calls are opt-in):
   - **Packages:** what's in each, and the comparison diagram.
   - **Models and messages:** `ChatOpenAI`, `AIMessage`, usage.
   - **Prompt templates:** variables, and where untrusted text goes.
   - **Composition:** `|`, `batch`, `RunnableLambda`.
   - **Structured output:** `include_raw`, and each failure case.
   - **Errors:** neutral exceptions, retries that multiply, fallbacks.
   - **Providers:** the same chain on Anthropic.
   - **Observability:** callbacks, and what LangSmith sends.
   - **Choosing:** testing, and the decision criteria.
2. [`notebooks/02-practice-quiz.ipynb`](notebooks/02-practice-quiz.ipynb): 10 self-check questions.

## 9. Independent assignment

[**Workbook: triage with LangChain, and an honest comparison**](workbook/assignment.md) (*Independent*: no AI coding assistant)

Implement `LangChainTriager` behind the `Triager` interface, make 52 new acceptance tests pass (most of them a contract run against both implementations), then measure the two versions and recommend one for this tool. The new files are in [`projects/03-llm-application/session-10`](../../projects/03-llm-application/README.md).

## 10. Expected deliverables

- The `incident-triage` project with `LangChainTriager`, tagged `session-10`.
- `uv run pytest` passing with no API key: 119 acceptance tests, unchanged, plus your own.
- `COMPARISON.md` with measurements and a recommendation; `NOTES.md` with your predictions and reflection.

## 11. Common mistakes

| Mistake | Instead |
|---|---|
| `ChatOpenAI()` without `model=` | Always pass the model from settings |
| `{report}` in the system message | The report in its own human message |
| `with_retry` on top of the SDK's retries | Retry in one place |
| Trusting `include_raw=True` to catch every bad output | Catch `ValidationError` too |
| Assuming LangChain's exceptions cover every status | A fallback clause, tested |
| Silent fallbacks | Record which path answered |
| Imports from internal modules | Public imports only |
| "Everyone uses it" as the reason | Measured criteria for this application |

## 12. Reading resources

Curated official documentation for this session: [`resources/references.md`](resources/references.md).

## 13. Reflection questions

1. Which part of LangChain would you miss most if you went back to the direct SDK? Which part wouldn't you miss?
2. What makes an abstraction "leaky", and where did you see it leak this session?
3. How would you keep a framework decision reversible in a large codebase?
4. When would a framework like LangChain be the wrong choice for a team, even if it fits the problem?

## 14. Interview questions

Practise answering these out loud, in two minutes or less each:

1. What is LangChain, and when would you not use it?
2. Explain LCEL. What does `prompt | model | parser` do?
3. How do you get structured output from an LLM with LangChain, and what can go wrong?
4. How do you handle retries and fallbacks in an LLM pipeline without making outages worse?
5. How would you switch an application from OpenAI to Anthropic, and what would you test?
6. How do you test code that uses LangChain?
7. How did you decide between a framework and a direct SDK in a past project?

## 15. Next-session preparation

**Session 11: Retrieval and RAG fundamentals** teaches retrieval-augmented generation: loading and chunking documents, embeddings, a vector store, and grounded answers with sources, partly with LangChain's components.

Before the session:

- Finish this workbook and tag `session-10`.
- If you plan to use local embeddings (fastembed, from Session 01 Part 9), run that part once now, so the model is downloaded (about 70 MB) before the session.
