# Session 06: References

Official documentation first. Each link says *why* it's worth your time, so you can pick what you need instead of reading everything.

## Pydantic

| Resource | Read it for |
|---|---|
| [Models](https://docs.pydantic.dev/latest/concepts/models/) | `BaseModel`, validation, `model_validate`, nested models and model configuration |
| [Fields](https://docs.pydantic.dev/latest/concepts/fields/) | Defaults, `default_factory`, constraints and aliases with `Field` |
| [Validators](https://docs.pydantic.dev/latest/concepts/validators/) | `field_validator` and `model_validator`, and the before, after and wrap modes |
| [Strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/) | Strictness per field and per model, and how JSON input differs |
| [Conversion table](https://docs.pydantic.dev/latest/concepts/conversion_table/) | Exactly which inputs each type accepts, in lax and in strict mode |
| [Serialization](https://docs.pydantic.dev/latest/concepts/serialization/) | `model_dump`, `model_dump_json`, `include`, `exclude` and modes |
| [Alias](https://docs.pydantic.dev/latest/concepts/alias/) | `alias`, `validation_alias`, `serialization_alias` and alias generators |
| [Validation errors](https://docs.pydantic.dev/latest/errors/validation_errors/) | Every error `type` code, with examples, for code that reacts to errors |
| [Models versus dataclasses](https://docs.pydantic.dev/latest/concepts/dataclasses/) | Pydantic dataclasses, and how they differ from `BaseModel` |
| [JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/) | `model_json_schema()`, which FastAPI uses for its documentation |

## Settings

| Resource | Read it for |
|---|---|
| [Settings management](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | `BaseSettings`, prefixes, `.env` files, parsing complex values and the order of precedence |
| [Secret types](https://docs.pydantic.dev/latest/api/types/#pydantic.types.SecretStr) | `SecretStr` and `get_secret_value()` |

## Background

| Resource | Read it for |
|---|---|
| [Python `typing.Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) | The type behind fixed allowed values |
| [The Twelve-Factor App: config](https://12factor.net/config) | Why services read configuration from the environment |
