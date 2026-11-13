# Session 07: References

Official documentation first. Each link says *why* it's worth your time, so you can pick what you need instead of reading everything.

## FastAPI tutorial

| Resource | Read it for |
|---|---|
| [First steps](https://fastapi.tiangolo.com/tutorial/first-steps/) | The smallest app, `fastapi dev`, and where `/docs` comes from |
| [Path parameters](https://fastapi.tiangolo.com/tutorial/path-params/) | Typed path parameters and route order |
| [Query parameters](https://fastapi.tiangolo.com/tutorial/query-params/) | Optional and required query parameters, and `bool` conversion |
| [Query parameters and string validations](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/) | `Annotated` with `Query(...)` constraints |
| [Query parameter models](https://fastapi.tiangolo.com/tutorial/query-param-models/) | Grouping filters in a Pydantic model, and forbidding extra parameters |
| [Request body](https://fastapi.tiangolo.com/tutorial/body/) | Pydantic models as request bodies |
| [Response model](https://fastapi.tiangolo.com/tutorial/response-model/) | Return types as response models, and how they filter output |
| [Response status code](https://fastapi.tiangolo.com/tutorial/response-status-code/) | `status_code=` and the `status` module |
| [Handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) | `HTTPException`, custom exception handlers and the `422` body |
| [Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) | `Depends`, `Annotated` aliases and sub-dependencies |
| [Bigger applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) | `APIRouter`, prefixes and tags, and splitting an app into modules |
| [Testing](https://fastapi.tiangolo.com/tutorial/testing/) | `TestClient` with pytest |

## FastAPI, beyond the tutorial

| Resource | Read it for |
|---|---|
| [Testing dependencies with overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/) | `app.dependency_overrides` |
| [Lifespan events](https://fastapi.tiangolo.com/advanced/events/) | Startup and shutdown code with a lifespan function |
| [Settings and environment variables](https://fastapi.tiangolo.com/advanced/settings/) | `pydantic-settings` with FastAPI, and caching settings with `lru_cache` |
| [Additional responses in OpenAPI](https://fastapi.tiangolo.com/advanced/additional-responses/) | Documenting `404` and `409` with `responses=` |
| [FastAPI CLI](https://fastapi.tiangolo.com/fastapi-cli/) | `fastapi dev`, `fastapi run`, and how the app is found |
| [Concurrency and async / await](https://fastapi.tiangolo.com/async/) | `def` versus `async def` endpoints; preparation for Session 08 |

## HTTP and API design

| Resource | Read it for |
|---|---|
| [MDN: HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status) | What each status code means, with examples |
| [RFC 9110: HTTP semantics, status codes](https://www.rfc-editor.org/rfc/rfc9110.html#name-status-codes) | The definitive source, including `409` and `422` |
| [OpenAPI specification](https://spec.openapis.org/oas/latest.html) | The format behind `/openapi.json`, for when you need to read it closely |
| [Uvicorn](https://uvicorn.dev/) | The ASGI server that runs FastAPI applications |

---

<!-- skillup-branding:start -->
## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center">
  <img src="../../../assets/diagrams/SkillUpWithSanjay.png" alt="#SkillUpWithSanjay logo" width="60">
</p>

<p align="center">
  <strong>#SkillUpWithSanjay</strong><br>
  <a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>
  &nbsp;&middot;&nbsp;
  <a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
</p>
<!-- skillup-branding:end -->
