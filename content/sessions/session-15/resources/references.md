# Session 15: References

Official documentation first. Each link says *why* it's worth your time. The capstone pins FastAPI 0.161, the OpenAI SDK 3.37 and Streamlit 1.66; when a page describes a different version, trust what your installed version does, and check it with a test.

## Generation

| Resource | Read it for |
|---|---|
| [OpenAI: structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs) | How `responses.parse` with `text_format` constrains the model to a schema, and how refusals arrive |

## The API

| Resource | Read it for |
|---|---|
| [FastAPI: handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) | `HTTPException`, and custom exception handlers for mapping your own errors to responses |
| [FastAPI: response model and return type](https://fastapi.tiangolo.com/tutorial/response-model/) | Why the route's return annotation shapes both the response and the `/docs` page |
| [Uvicorn: settings](https://uvicorn.dev/settings/) | `--factory`, `--host`, `--port` and `--reload` |

## The UI

| Resource | Read it for |
|---|---|
| [Streamlit: basic concepts](https://docs.streamlit.io/get-started/fundamentals/main-concepts) | The rerun model: your script runs top to bottom on every interaction |
| [Working with Streamlit's execution model](https://docs.streamlit.io/develop/concepts/architecture) | Reruns, the client-server split, and what that means for your code |
| [Caching overview](https://docs.streamlit.io/develop/concepts/architecture/caching) | `st.cache_resource` versus `st.cache_data`, and when each is safe |
| [Session state](https://docs.streamlit.io/develop/concepts/architecture/session-state) | Keeping values, such as the last answer, across reruns for one user |
| [`config.toml`](https://docs.streamlit.io/develop/api-reference/configuration/config.toml) | Every setting, including `browser.gatherUsageStats` and `server.address` |
| [App testing](https://docs.streamlit.io/develop/concepts/app-testing) and [getting started with it](https://docs.streamlit.io/develop/concepts/app-testing/get-started) | `AppTest`: running a page in pytest, typing into widgets and reading elements |

## In the course

- Session 09's [concepts notebook](../../session-09/notebooks/01-concepts.ipynb): structured output, provider errors and HTTP-level fakes.
- Session 11's [concepts notebook](../../session-11/notebooks/01-concepts.ipynb): numbered contexts, citations and evaluation.
- Session 07's [workbook](../../session-07/workbook/assignment.md): FastAPI routes, models and tests.
- Session 14's [concepts notebook](../../session-14/notebooks/01-concepts.ipynb): the index this session reads.
