# Session 09: References

Official documentation first. Each link says *why* it's worth your time, so you can pick what you need instead of reading everything. Provider documentation changes often; if a page has moved, search the provider's docs for its title.

## OpenAI

| Resource | Read it for |
|---|---|
| [Text generation](https://developers.openai.com/api/docs/guides/text) | The Responses API: instructions, input, and reading the output |
| [Structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs) | JSON schemas, `responses.parse` with Pydantic, refusals, and schema limitations |
| [Responses API reference](https://developers.openai.com/api/reference/resources/responses) | Every request parameter and response field, including `status`, `incomplete_details` and `usage` |
| [Error codes](https://developers.openai.com/api/docs/guides/error-codes) | What each HTTP status means for this API, and what to do about it |
| [Rate limits](https://developers.openai.com/api/docs/guides/rate-limits) | Requests and tokens per minute, the rate-limit headers, and backing off |
| [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) | Why a fixed prompt prefix is cheaper, and how to keep yours cacheable |
| [Pricing](https://developers.openai.com/api/docs/pricing) | Input, output and cached-input prices per model |
| [openai-python on GitHub](https://github.com/openai/openai-python) | The SDK's README: timeouts, retries, error classes, and custom HTTP clients |

## Anthropic

| Resource | Read it for |
|---|---|
| [Messages API reference](https://platform.claude.com/docs/en/api/messages) | The Anthropic request and response, for comparison with OpenAI's |
| [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) | `output_format` with Pydantic models in the Anthropic SDK |

## Security and Python

| Resource | Read it for |
|---|---|
| [OWASP: LLM01 Prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | How prompt injection works, direct and indirect, and layered mitigations |
| [Python `typing`, including `Protocol`](https://docs.python.org/3.13/library/typing.html#typing.Protocol) | Structural interfaces, used for the `Triager` protocol |

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
