# Session 13: References

Official documentation first. Claude Code changes quickly: when something behaves differently from what you read here or in the notebook, check `claude --version` and the current documentation. Each link says *why* it's worth your time.

## Getting started

| Resource | Read it for |
|---|---|
| [Claude Code overview](https://code.claude.com/docs/en/overview) | What Claude Code is, and where it runs: terminal, IDEs, desktop, web |
| [Advanced setup](https://code.claude.com/docs/en/setup) | Installation on macOS, Linux and Windows, the accounts it needs, and updates |
| [Quickstart](https://code.claude.com/docs/en/quickstart) | A guided first session |

## Working well with an assistant

| Resource | Read it for |
|---|---|
| [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) | **Read this one in full.** Giving the assistant a check it can run, explore then plan then code, specific prompts, managing context, and common failure patterns |
| [Common workflows](https://code.claude.com/docs/en/common-workflows) | Step-by-step recipes: understanding a codebase, fixing bugs, refactoring, tests, pull requests |
| [How Claude remembers your project](https://code.claude.com/docs/en/memory) | `CLAUDE.md`, `AGENTS.md`, `/init`, and what loads when |
| [Explore the context window](https://code.claude.com/docs/en/context-window) | What fills the context, and why it matters |
| [Checkpointing](https://code.claude.com/docs/en/checkpointing) | `/rewind`: what it can restore, and why it doesn't replace Git |
| [Commands](https://code.claude.com/docs/en/commands) | Every slash command, including `/init`, `/context`, `/clear`, `/compact`, `/rewind`, `/plan` and `/usage` |
| [Review locally with /code-review](https://code.claude.com/docs/en/code-review-local) | What the review covers, how to choose its target, and its limits |

## Control and safety

| Resource | Read it for |
|---|---|
| [Choose a permission mode](https://code.claude.com/docs/en/permission-modes) | The modes, what each runs without asking, and which mode a session starts in |
| [Configure permissions](https://code.claude.com/docs/en/permissions) | Allow, ask and deny rules, and how they combine with modes |
| [Security](https://code.claude.com/docs/en/security) | Claude Code's protections against prompt injection, and best practices for untrusted content |
| [Data usage](https://code.claude.com/docs/en/data-usage) | What's sent where, retention, and the training policy for consumer and commercial accounts |
| [Manage costs effectively](https://code.claude.com/docs/en/costs) | `/usage`, and how to reduce token use |
| [Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide) | Deterministic checks that run every time; for the hook extension challenge |
| [OWASP: LLM01 Prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | Direct and indirect prompt injection, and layered mitigations (also in Session 09) |

## Reviewing code

| Resource | Read it for |
|---|---|
| [mutmut](https://mutmut.readthedocs.io/) | A mutation-testing tool for Python, automating what the concepts notebook did by hand |
| [`warnings`](https://docs.python.org/3.13/library/warnings.html) | Turning deprecation warnings into errors to find outdated APIs |
| [`statistics.quantiles`](https://docs.python.org/3.13/library/statistics.html#statistics.quantiles) | The `exclusive` and `inclusive` methods from the concepts notebook's Common Mistake |

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
