# Pydantic Patterns

Pydantic (version 2, as used throughout the course) turns untrusted data into typed objects, or tells you exactly what's wrong with it. Use it at the **edges** of your program: files, HTTP requests and responses, settings, and LLM output. Session 06 teaches it; this page collects the patterns.

## A model

```python
from datetime import datetime
from typing import Literal

from pydantic import AwareDatetime, BaseModel, Field, ValidationError

Priority = Literal["P1", "P2", "P3", "P4"]


class Assignee(BaseModel):
    name: str = Field(min_length=1)
    email: str | None = None  # optional, with a default


class Ticket(BaseModel):
    id: str = Field(pattern=r"^INC-\d+$")
    priority: Priority
    team: str
    opened_at: AwareDatetime  # a datetime that must have a time zone
    tags: list[str] = []  # safe in Pydantic: each instance gets its own copy
    assignee: Assignee | None = None  # a nested model


ticket = Ticket.model_validate(
    {
        "id": "INC-7",
        "priority": "P2",
        "team": "network",
        "opened_at": "2026-11-02T09:30:00+01:00",
        "assignee": {"name": "Amara"},
    }
)
print(
    ticket.opened_at.utcoffset(),
    ticket.assignee.name,
    isinstance(ticket.opened_at, datetime),
)

try:
    Ticket.model_validate(
        {"id": "7", "priority": "P9", "team": "network", "opened_at": "soon"}
    )
except ValidationError as error:
    for problem in error.errors(include_url=False):
        print(problem["loc"], problem["msg"])
```

- One `ValidationError` lists **every** problem, each with its location (`loc`) and message.
- `Field(...)` adds constraints: `min_length`, `max_length`, `ge`, `le`, `pattern`.
- `Literal[...]` restricts a field to fixed values; an `Enum` works too.
- `X | None = None` makes a field optional. `X | None` **without** a default means "required, but may be `null`".

## Parsing and serialising

| Task | Code |
|---|---|
| From a dict | `Ticket.model_validate(data)` |
| From a JSON string or bytes | `Ticket.model_validate_json(text)` |
| To a dict (Python types) | `ticket.model_dump()` |
| To a JSON-ready dict | `ticket.model_dump(mode="json")`: datetimes become strings |
| To a JSON string | `ticket.model_dump_json()` |
| Leave out unset or empty fields | `model_dump(exclude_none=True)`, `exclude_unset=True` |
| A list of models | `TypeAdapter(list[Ticket]).validate_python(rows)` |
| A changed copy | `ticket.model_copy(update={"team": "dns"})` |

## Custom rules

```python
from pydantic import BaseModel, field_validator, model_validator


class Window(BaseModel):
    start_hour: int
    end_hour: int
    owner: str

    @field_validator("owner")
    @classmethod
    def owner_is_trimmed(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")  # becomes part of the ValidationError
        return value  # the returned value is what's stored

    @model_validator(mode="after")
    def ends_after_start(self) -> "Window":  # rules that need several fields
        if self.end_hour <= self.start_hour:
            raise ValueError("end_hour must be after start_hour")
        return self


print(Window(start_hour=9, end_hour=17, owner="  network  ").owner)
```

Raise `ValueError` (not your own exception type) inside validators: Pydantic turns it into a `ValidationError` entry.

## Strictness and unknown fields

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Lax(BaseModel):
    count: int


class Strict(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
    count: int


print(Lax(count="3").count)  # "3" is coerced to 3 in the default (lax) mode
for data in ({"count": "3"}, {"count": 3, "typo": 1}):
    try:
        Strict.model_validate(data)
    except ValidationError as error:
        print(error.errors(include_url=False)[0]["type"])
```

| Setting | Effect | Use it for |
|---|---|---|
| `extra="forbid"` | Unknown fields are errors | Requests and configuration, where a typo should fail |
| `extra="ignore"` (default) | Unknown fields are dropped | Third-party responses that grow new fields |
| `strict=True` | No type coercion (`"3"` isn't an `int`) | When the source should already be typed |
| `frozen=True` | Instances are immutable and hashable | Values you pass around and compare |

## Settings

```python
import os

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="INCIDENT_", env_file=".env", extra="ignore"
    )

    api_url: str = "https://assets.example.com"
    timeout_seconds: float = 5.0
    api_token: SecretStr | None = None  # printed as '**********'


os.environ["INCIDENT_TIMEOUT_SECONDS"] = "2.5"
os.environ["INCIDENT_API_TOKEN"] = "not-a-real-token"
settings = Settings()
print(settings.timeout_seconds, settings.api_token)
```

- Environment variables win over `.env`, which wins over defaults. Names are matched case-insensitively.
- A value that can't be parsed raises `ValidationError`; a complex value (a list or dict) that isn't valid JSON raises `pydantic_settings.SettingsError`. Catch both at startup.
- Use `SecretStr` for keys and tokens, and `.get_secret_value()` only where the value is sent.

## Common mistakes

| Mistake | Better |
|---|---|
| Pydantic v1 code from old answers: `.dict()`, `.parse_obj()`, `@validator`, `class Config:` | `.model_dump()`, `.model_validate()`, `@field_validator`, `model_config = ConfigDict(...)` |
| Validating deep inside the program | Validate once, at the edge; pass models inward |
| `datetime` for timestamps from outside | `AwareDatetime`, so a time without a zone is rejected |
| Catching `ValidationError` and printing `str(error)` to users | Map `error.errors()` to your own messages; the raw text can echo the input |
| One model for the request, the response and the database | Separate input and output models when they differ (an `id` the server assigns, a field it hides) |

## Further reading

- [Pydantic: models](https://docs.pydantic.dev/latest/concepts/models/), [validators](https://docs.pydantic.dev/latest/concepts/validators/) and [settings management](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).
- [Pydantic: migration guide from v1](https://docs.pydantic.dev/latest/migration/), for recognising old code.
