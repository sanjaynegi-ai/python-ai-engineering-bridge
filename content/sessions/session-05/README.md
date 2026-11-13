# Session 05: HTTP and API Integration

**Phase 2: Professional Python Applications**

## Session overview

Phase 2 starts by connecting your code to other people's services. You'll call REST APIs with **HTTPX**, decide deliberately what each status code and failure means, keep credentials in the environment instead of the code, and wrap an API in a small client class that the rest of your application can trust. Then you'll test that client with **respx**, without touching the network.

The running example is the fictional Orbital Logistics **Asset Inventory**, which the incident tooling needs in order to know who owns a broken system and how critical it is. The client you build in the workbook is reused by the incident API service in Session 07.

## Why this matters

AI engineering is integration engineering. Every LLM provider, vector database, document store and internal system you'll connect to is an HTTP API, often wrapped in an SDK that is itself built on HTTPX. The failure modes are always the same: slow answers, outages, rate limits, rejected credentials, and responses that aren't what the documentation promised.

Code that ignores them hangs at 02:00, crashes on the first `503`, or leaks a key into a log file. Code that handles them is boring in production, which is the goal. This session gives you the patterns you'll reuse in Session 09, when the API on the other end is a language model that costs money per call.

## Prerequisites

**Knowledge:** Sessions 01–04. Project 01 is complete: you're comfortable with a `src/`-layout package, dataclasses, custom exceptions and pytest fixtures.

**Before the session:**

1. In the course repository, run `uv sync`. It adds HTTPX and respx (the course environment's `web` group) to your notebook kernel.
2. Check that `notebooks/01-concepts.ipynb` runs its first two code cells. They start a small fake service on your machine, so no internet access is needed.

## Learning objectives

By the end of this session you will be able to:

1. **Call** REST APIs with HTTPX: a reusable `httpx.Client`, `GET` and `POST`, query parameters, JSON bodies and headers.
2. **Explain** the phases of an HTTP request and their timeouts, and **configure** timeouts deliberately.
3. **Map** status codes and transport errors to decisions (not found, unauthorised, unavailable, unexpected), and **implement** that mapping with chained domain exceptions.
4. **Load** credentials from environment variables and `.env`, and **prevent** them from appearing in code, `repr()`, logs or error messages.
5. **Design** an API client class with domain methods, domain return types, one shared HTTP client and an injectable transport.
6. **Test** an API client with `httpx.MockTransport` and respx, covering success, 4xx, 5xx, timeouts and connection failures.
7. **Decide** which requests can safely be retried.


## Concepts covered

| Concept | Depth |
|---|---|
| HTTP request phases, status code classes | Independent implementation |
| HTTPX: `httpx.Client`, `base_url`, headers, `params`, `json`, `Response` | Independent implementation |
| Timeouts per phase; HTTPX's exception hierarchy | Independent implementation |
| Status-code-to-decision mapping; domain exceptions with chaining | Independent implementation |
| Environment variables, python-dotenv, `.env.example`, keeping secrets out of output | Independent implementation |
| API client design: one shared client, context manager, injectable transport, pagination | Independent implementation |
| Testing with `httpx.MockTransport` and respx | Independent implementation |
| Retries, backoff and idempotency | Awareness |
| Command-line subcommands with `argparse` | Awareness (provided in the workbook) |



## Guided exercises

1. [`notebooks/01-concepts.ipynb`](notebooks/01-concepts.ipynb):
   - **The fake inventory:** make authenticated, paginated and `POST` requests.
   - **Failures:** predict what `raise_for_status()`, a timeout and a refused connection do.
   - **`.env` precedence:** predict which value wins.
   - **A minimal client:** translate HTTP outcomes into three domain errors.
   - **Debugging:** find out why the enrichment is slow.
   - **Testing:** the same client against `MockTransport` and respx.
   - **Retries (awareness):** a backoff helper against a flaky fake.
2. [`notebooks/02-practice-quiz.ipynb`](notebooks/02-practice-quiz.ipynb): 10 self-check questions.

## Independent assignment

[**Workbook: an Asset Inventory client**](workbook/assignment.md) (*Independent*: no AI coding assistant)

Implement settings loading and an `InventoryClient` for the fake Asset Inventory: authentication, timeouts, error translation, pagination and a `POST` endpoint. Make 46 provided acceptance tests pass (including integration tests against the real fake server), write at least 10 respx tests of your own, and verify that the token never leaks. A ready-made `asset-lookup` command lets you use your client against the running fake server.

## Expected deliverables

- The `asset-lookup` project with `settings.py` and `client.py` implemented and tagged `session-05`.
- `uv run pytest` passing: 46 acceptance tests, unchanged, plus at least 10 of your own.
- The `asset-lookup` command producing the documented exit codes against the fake server.
- `.env` git-ignored and absent from the submission; `NOTES.md` with your answers and reflection.

## Common mistakes

| Mistake | Instead |
|---|---|
| No timeout | Always set one; HTTPX's default is 5 seconds, `requests` has none |
| A new client per request | One `httpx.Client`, reused, closed with `with` |
| Treating any response as success | Check `status_code`, or call `raise_for_status()` |
| `except Exception:` around HTTP calls | Catch `httpx.TransportError`; branch on status codes |
| Query strings built with f-strings | `params={...}` |
| Retrying `POST` after a timeout | Retry only idempotent reads, with backoff |
| Token in code, `.env.example`, logs or messages | Environment variables, `field(repr=False)`, name the variable but never the value |
| Tests that call the real service | `MockTransport` or respx |

## Reading resources

Curated official documentation for this session: [`resources/references.md`](resources/references.md).

## Reflection questions

1. Which failure would hurt your current team's integrations most: no timeouts, swallowed errors, or leaked credentials? What would you change first?
2. Where should the decision "the inventory is down, produce the report anyway" live: in the client, or in the code that calls it? Why?
3. What's the difference between a test with respx and a test against the fake server? Would you run both in CI?
4. How would you explain idempotency to a colleague deciding whether to retry a request?

## Interview questions

Practise answering these out loud and support each answer with clear engineering reasoning:

1. What happens if you call an HTTP API without a timeout? What timeouts exist?
2. How do you handle a `503` versus a `404` versus a `401` from an API you depend on?
3. Why should an application reuse one HTTP client instead of creating one per request?
4. How do you keep API keys out of source code, logs and error messages?
5. How would you unit-test code that calls a third-party API?
6. Which requests is it safe to retry, and how?
7. What does `raise ... from error` give you when wrapping an HTTP library's exceptions?

## Next-session preparation

**Session 06: Pydantic and Data Validation** replaces the hand-written checks you've written since Session 03, such as `validate_record`, `Asset.from_json` and `load_settings`, with Pydantic models and `pydantic-settings`, which validate, convert and document data in one place.

Before the session:

- Finish this workbook. Session 06 converts your `Asset` and `Settings` to Pydantic models.
- Count the lines in your Session 03 `validate_record` and this session's `load_settings`. You'll compare them with their Pydantic equivalents.

---

<!-- skillup-branding:start -->
## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center">
  <img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="#SkillUpWithSanjay logo" width="60">
</p>

<p align="center">
  <strong>#SkillUpWithSanjay</strong><br>
  <a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>
  &nbsp;&middot;&nbsp;
  <a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
</p>
<!-- skillup-branding:end -->
