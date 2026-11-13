# Session 06: Pydantic and Data Validation

**Phase 2: Professional Python Applications** · **Project 02 begins**

## Session overview

Since Session 03 you've validated data by hand: ticket records, configuration files, API responses and settings. This session replaces all of it with **Pydantic**: you declare what valid data looks like, as a class with type hints, and Pydantic validates, converts, normalises, reports errors and serialises it. **pydantic-settings** does the same for configuration from environment variables.

The workbook starts **Project 02**, the incident service, by rebuilding Project 01's data layer with Pydantic models. In Session 07 those same models become a FastAPI service's request and response schemas.

## Why this matters

Every boundary in an AI application needs a data contract: records from files, HTTP requests and responses, configuration, and above all **LLM output**, which arrives as "almost JSON" more often than anyone would like. Pydantic is the standard tool for those contracts in Python. FastAPI, the OpenAI and Anthropic SDKs, LangChain and many others are built on it.

Knowing it well means you can read those libraries' types, write models that fail loudly at the edge instead of quietly in the middle, and turn validation errors into messages people can act on.

## Prerequisites

**Knowledge:** Sessions 01–05. In particular, Session 03's hand validation and Session 05's settings and secrets.

**Before the session:**

1. In the course repository, run `uv sync`. It adds Pydantic and pydantic-settings to the notebook kernel.
2. Have the Project 01 checkpoint (`projects/01-python-data-processor/checkpoint/`) or your own Project 01 at hand, for comparison.

## Learning objectives

By the end of this session you will be able to:

1. **Define** Pydantic models with typed, required, optional, defaulted, constrained and nested fields.
2. **Choose** between lax and strict conversion for a field, and **justify** the choice for a given data source.
3. **Interpret** a `ValidationError`, and **map** its errors to user-facing messages.
4. **Write** `field_validator` and `model_validator` rules for normalisation and business constraints.
5. **Serialise** models with `model_dump` and `model_dump_json`, controlling aliases, inclusions and exclusions.
6. **Load** typed configuration, including secrets, from environment variables and `.env` with `pydantic-settings`, and **handle** both kinds of settings failure.
7. **Decide** when to use a Pydantic model and when a dataclass.


## Concepts covered

| Concept | Depth |
|---|---|
| `BaseModel`, `model_validate`, `model_validate_json` | Independent implementation |
| Required, nullable and defaulted fields; `default_factory` | Independent implementation |
| `Field` constraints, `Literal`, nested models, `extra` handling | Independent implementation |
| Lax and strict conversion | Independent implementation |
| `ValidationError.errors()`: `loc`, `type`, `msg`; mapping to messages | Independent implementation |
| `field_validator` (after and before modes), `model_validator` | Independent implementation |
| `model_dump`, `model_dump_json`, `include`, `exclude`, `exclude_none`, aliases | Independent implementation |
| `BaseSettings`, `env_prefix`, `.env`, `SecretStr`, `SettingsError` | Independent implementation |
| Alias generators, JSON Schema, advanced configuration | Working knowledge |



## Guided exercises

1. [`notebooks/01-concepts.ipynb`](notebooks/01-concepts.ipynb):
   - **First model:** conversion, and one error per problem.
   - **Required versus optional:** predict which inputs fail.
   - **Lax versus strict:** a table of inputs to predict.
   - **Error messages:** a `describe()` helper for data owners.
   - **Validators:** normalisation, a before-validator, a cross-field rule.
   - **Serialisation and aliases:** a camelCase API, and round trips.
   - **Settings:** environment and `.env` precedence, `SecretStr`, two kinds of failure.
2. [`notebooks/02-practice-quiz.ipynb`](notebooks/02-practice-quiz.ipynb): 10 self-check questions.

## Independent assignment

[**Workbook: Project 02 begins, contracts with Pydantic**](workbook/assignment.md) (*Independent*: no AI coding assistant)

Starting from the Project 01 checkpoint, replace hand validation with a `Ticket` model, build rejections from `ValidationError`, turn the report into nested models, and replace `config.json` with `pydantic-settings`, all while producing exactly the same report. 53 acceptance tests are provided, one file per milestone, and you write at least 10 of your own. The starter is in [`projects/02-python-api-service`](../../projects/02-python-api-service/README.md).

## Expected deliverables

- The `incident-api` project with `models.py`, `settings.py`, `report.py` and `load_exports` implemented, tagged `session-06`.
- `uv run pytest` passing: 53 acceptance tests, unchanged, plus at least 10 of your own.
- `NOTES.md` comparing the hand-written and declarative versions, with your reflection.

## Common mistakes

| Mistake | Instead |
|---|---|
| A nullable field without a default, expected to be optional | Add `= None` |
| Lax mode on typed contracts | `Field(strict=True)` where a type mismatch is a bug |
| A validator without `return` | Always return the value |
| Raising custom exceptions in validators | Raise `ValueError` |
| Showing `str(error)` to users | Map `error.errors()` to `field: message` lines |
| Matching on `msg` in code | Match on `type` |
| `extra="forbid"` on other teams' data | `"ignore"` for theirs, `"forbid"` for your own inputs |
| Secrets as `str` in settings | `SecretStr` |
| Catching only `ValidationError` around `Settings()` | Also catch `pydantic_settings.SettingsError` |

## Reading resources

Curated official documentation for this session: [`resources/references.md`](resources/references.md).

## Reflection questions

1. Which of your hand-written validators from Sessions 03–05 would have benefited most from Pydantic, and why?
2. Where is the line between a validation rule and business logic? Should "SLA hours must increase" live in the settings model, or in the code that uses it?
3. When could strict mode cause problems in production, and how would you notice?
4. What would you need to change if an exporting system started sending a new field?

## Interview questions

Practise answering these out loud and support each answer with clear engineering reasoning:

1. What does Pydantic do that dataclasses don't? When would you use each?
2. Explain lax versus strict validation, with an example of when each is right.
3. How do you validate a rule that involves two fields?
4. How would you return validation errors from an API in a way clients can use?
5. How do you load configuration from the environment safely, including secrets?
6. What are aliases for, and when do you need them?
7. Your service receives JSON from a partner that occasionally sends numbers as strings. What do you do?

## Next-session preparation

**Session 07: FastAPI** puts your Project 02 models behind an HTTP API: routes, path and query parameters, request and response models, dependency injection, error handling, automatic documentation, and tests with `TestClient`.

Before the session:

- Finish this workbook and tag it. Session 07 adds an `api` module to the same project.
- Run `uv run python -c "from incident_api.models import Ticket; import json; print(json.dumps(Ticket.model_json_schema(), indent=2))"` in your project, and look at the output. FastAPI will publish exactly that as API documentation.

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
