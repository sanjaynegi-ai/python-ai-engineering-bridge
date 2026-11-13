# Session 10: References

Official documentation first. Each link says *why* it's worth your time, so you can pick what you need instead of reading everything. LangChain changes quickly: check that what you read matches the versions in your lockfile.

## LangChain

| Resource | Read it for |
|---|---|
| [LangChain overview](https://docs.langchain.com/oss/python/langchain/overview) | What the framework is for, and how the packages fit together |
| [Install LangChain](https://docs.langchain.com/oss/python/langchain/install) | The package split: core, integrations, `langchain` |
| [Models](https://docs.langchain.com/oss/python/langchain/models) | Chat models, `init_chat_model`, invoking and batching, and model parameters |
| [Messages](https://docs.langchain.com/oss/python/langchain/messages) | Message types, content blocks and usage metadata |
| [Structured output](https://docs.langchain.com/oss/python/langchain/structured-output) | `with_structured_output`, methods and `include_raw` |
| [ChatOpenAI integration](https://docs.langchain.com/oss/python/integrations/chat/openai) | `ChatOpenAI` options, including the Responses API |
| [ChatAnthropic integration](https://docs.langchain.com/oss/python/integrations/chat/anthropic) | The Anthropic integration, for the provider-switch extension |

## API reference

| Resource | Read it for |
|---|---|
| [`langchain_core.runnables`](https://reference.langchain.com/python/langchain-core/runnables) | The runnable interface: `invoke`, `batch`, `stream`, `with_retry`, `with_fallbacks`, `RunnableLambda` |
| [`langchain_core.prompts`](https://reference.langchain.com/python/langchain-core/prompts) | `ChatPromptTemplate` and its variables |
| [`langchain_core.exceptions`](https://reference.langchain.com/python/langchain-core/exceptions) | The provider-neutral exceptions, such as `ModelRateLimitError` |

## Observability

| Resource | Read it for |
|---|---|
| [LangSmith observability](https://docs.langchain.com/langsmith/observability) | What tracing records, and how it's switched on, so you can decide whether you may use it |

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
