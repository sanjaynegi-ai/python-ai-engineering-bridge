# Session 09: Direct LLM API Integration

**Phase 3: Python for AI Applications** · **Project 03 begins**

## Session overview

This session calls a large language model from Python directly, with the provider's SDK and no framework. You'll see an LLM API for what it is from an engineer's side: an HTTP API that's slow, metered by the token, occasionally unavailable, and whose output must be validated before you trust it. You'll get **structured output** as a Pydantic model, handle refusals, truncation and rule-breaking output, record what each request costs, and test it all without an API key.

The workbook starts **Project 03**: an incident-triage tool that turns free-text reports into validated, structured triage.

## Why this matters

Most AI features in real products are a direct LLM call wrapped in ordinary engineering: configuration, validation, error handling, cost control and tests. Frameworks (Session 10) are built on the same calls, so understanding them directly is what lets you debug a framework when it misbehaves.

Many AI prototypes fail in production for engineering reasons rather than model quality: no timeout, unvalidated output, a crash on the first refusal, a surprise invoice, a prompt injection. This session addresses each of these.

## Prerequisites

**Knowledge:** Sessions 01–08. In particular, Session 01 Part 8 (providers and keys), Session 05 (HTTP clients, errors, mocking), Session 06 (Pydantic) and Session 08 (partial failure).

Before you begin:

1. In the course repository, run `uv sync`.
2. **Optional:** an OpenAI API key in the course repository's `.env`, as set up in Session 01 Part 8, with a monthly budget set in the provider's dashboard. Everything in this session also works without a key, against fakes.
3. Finish Project 02 (Session 08).

## Learning objectives

By the end of this session you will be able to:

1. **Explain** the request and response of an LLM API: instructions, input, model, output token limit, status, output and usage.
2. **Configure** an SDK client with credentials from the environment, an explicit timeout and retries, and **explain** which failures it retries.
3. **Design** an output contract as a Pydantic model, and **obtain** validated structured output with `responses.parse`.
4. **Handle** refusals, truncated output and rule-breaking output, and **map** SDK exceptions to application error types.
5. **Calculate** the cost of a request and a workload from token usage.
6. **Test** LLM code without paid calls, with fakes at the interface and HTTP levels, and **validate** the fakes against the SDK's types.
7. **Recognise** prompt injection, and **apply** basic mitigations.

## Concepts covered

| Concept | Depth |
|---|---|
| The Responses API: `instructions`, `input`, `max_output_tokens`, `status`, `output`, `usage` | Independent implementation |
| Client configuration: keys, timeouts, retries | Independent implementation |
| Structured outputs with `responses.parse` and Pydantic | Independent implementation |
| Refusals, truncation, contract violations; error mapping | Independent implementation |
| Tokens, prices and cost | Independent implementation |
| `typing.Protocol`; fakes at the interface and HTTP levels | Independent implementation |
| Chat Completions and the Anthropic Messages API | Working knowledge |
| Conversations, reasoning tokens, prompt caching | Awareness |
| Prompt injection and data protection | Awareness, with basic mitigations applied |

## Guided exercises

1. [`notebooks/01-concepts.ipynb`](notebooks/01-concepts.ipynb) (runs free against an example API; live calls are opt-in):
   - **Anatomy:** one call, the request and response, and three providers compared.
   - **Reliability:** timeouts, retries and the SDK's exceptions.
   - **Structured output:** a Pydantic contract, and the four checks.
   - **Failures:** refusal, truncation, rule-breaking output.
   - **Cost:** tokens, prices and monthly estimates.
   - **Testing:** a `Protocol`, three kinds of test double, and checking fakes.
   - **Security:** prompt injection and data protection.
   - **Anthropic:** the same call with another SDK.
2. [`notebooks/02-practice-quiz.ipynb`](notebooks/02-practice-quiz.ipynb): 10 self-check questions.

## Independent assignment

[**Workbook: Project 03 begins, LLM-assisted triage**](workbook/assignment.md) (*Independent*: no AI coding assistant)

Design the triage contract, implement `OpenAITriager` with full error mapping, write the batch service, and compare the LLM with a keyword baseline. 67 acceptance tests are provided, and none of them needs an API key. The starter is in [`projects/03-llm-application`](../../projects/03-llm-application/README.md).

## Expected deliverables

- The `incident-triage` project with `TriageResult`, `Usage`, `Settings`, `OpenAITriager` and `triage_all` implemented, tagged `session-09`.
- `uv run pytest` passing with no key: 67 acceptance tests, unchanged, plus at least 8 of your own.
- `NOTES.md` with the baseline analysis, the comparison and your reflection.

## Common mistakes

| Mistake | Instead |
|---|---|
| Keeping the SDK's 10-minute default timeout | A timeout that fits the caller |
| Adding a retry loop around the SDK's retries | Configure `max_retries`; stop on configuration errors |
| Using `output_parsed` without checking for a refusal | Check for `None` and a refusal first |
| Trusting the schema to enforce every rule | Validators in the Pydantic model |
| Report text inside the instructions | Untrusted text only in `input` |
| Repeating the provider's error message | Your own message: it can contain part of the key |
| Not recording usage | Tokens per request, totalled per run |
| Tests that call the real API | Fakes; check them against the SDK's types |

## Reading resources

Curated official documentation for this session: [`resources/references.md`](resources/references.md).

## Reflection questions

1. Which of the failure cases in this session have you seen in production integrations in your own work, with other APIs?
2. Where would a wrong triage cause real harm, and how would you design for that?
3. What would you need to know before sending real incident reports to an external LLM provider?
4. Is the cost of this tool worth it compared with a person's time? What would you measure to decide?

## Interview questions

Practise answering these out loud and support each answer with clear engineering reasoning:

1. Walk through an LLM API request and response. What does each field do?
2. How do you get reliable structured data out of an LLM?
3. What can go wrong with an LLM call, and how does your code handle each case?
4. How do you estimate and control the cost of an LLM feature?
5. How do you test code that calls an LLM?
6. What is prompt injection, and how do you reduce the risk?
7. When would you call a provider's SDK directly rather than use a framework such as LangChain?

## Next-session preparation

**Session 10: LangChain fundamentals** rebuilds this session's triage with LangChain: prompt templates, chat models, structured output and composition. You'll compare the two versions on code size, debuggability, testability and lock-in.

Before continuing:

- Finish this workbook and tag `session-09`.
- Write down, in a few lines, what you'd want a framework to do for you, having written the direct version.

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
