# Session 05: References

Official documentation first. Each link says *why* it's worth your time, so you can pick what you need instead of reading everything.

## HTTPX

| Resource | Read it for |
|---|---|
| [QuickStart](https://www.python-httpx.org/quickstart/) | Requests, query parameters, JSON, headers, status codes, `raise_for_status()` |
| [Clients](https://www.python-httpx.org/advanced/clients/) | Why and how to use `httpx.Client`: base URLs, shared headers, connection pooling |
| [Timeouts](https://www.python-httpx.org/advanced/timeouts/) | The four timeouts, the 5-second default, and fine-grained configuration |
| [Exceptions](https://www.python-httpx.org/exceptions/) | The full exception hierarchy, as drawn in this session's diagram |
| [Transports](https://www.python-httpx.org/advanced/transports/) | `HTTPTransport(retries=...)` and `MockTransport` |
| [Event hooks](https://www.python-httpx.org/advanced/event-hooks/) | Logging requests and responses (workbook extension 3) |
| [Requests compatibility](https://www.python-httpx.org/compatibility/) | The differences from `requests`, which you'll meet in other codebases |

## Testing HTTP code

| Resource | Read it for |
|---|---|
| [respx: user guide](https://lundberg.github.io/respx/guide/) | Routes, patterns, `side_effect`, and call assertions |
| [respx: API reference](https://lundberg.github.io/respx/api/) | Everything `respond()`, `mock()` and the router accept |

## HTTP itself

| Resource | Read it for |
|---|---|
| [MDN: HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status) | What each status code means, with the classes summarised |
| [MDN: idempotent methods](https://developer.mozilla.org/en-US/docs/Glossary/Idempotent) | Which methods are safe to repeat, and why that matters for retries |
| [MDN: Retry-After](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After) | How servers tell clients when to try again |
| [MDN: Authorization](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Authorization) | The `Bearer` scheme and other authentication schemes |

## Configuration and secrets

| Resource | Read it for |
|---|---|
| [python-dotenv](https://saurabh-kumar.com/python-dotenv/) | `load_dotenv`, `override`, and the `.env` file format |
| [`os.environ`](https://docs.python.org/3/library/os.html#os.environ) | Reading environment variables in Python |
| [The Twelve-Factor App: config](https://12factor.net/config) | The reasoning behind keeping configuration in the environment |
| [GitHub: removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) | What to do if a secret was committed (revoke it first) |

## Command-line tools

| Resource | Read it for |
|---|---|
| [`argparse` tutorial](https://docs.python.org/3/howto/argparse.html) | How the provided `cli.py` defines its subcommands |

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
