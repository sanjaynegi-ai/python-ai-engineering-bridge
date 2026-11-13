# Session 13: Claude Code for Professional Engineering

**Phase 4: AI-Assisted Engineering and RAG Capstone**

## Session overview

For twelve sessions you've written Python yourself, so that you can judge Python. This session adds an AI coding assistant, **Claude Code**, to your workflow: exploring a repository, planning a change, implementing and testing it, and reviewing the result, through **Understand → Plan → Implement → Test → Review → Explain**.

The emphasis is on the parts that stay yours: writing requests an assistant can act on, keeping it within safe permissions, and reviewing what it produces with evidence. The workbook has two parts: an **AI-assisted** feature for Project 03, and an **AI-review** of a pull request an assistant wrote, with problems that its own tests don't show.

## Why this matters

AI coding assistants are now part of professional software engineering, and AI Engineering roles expect fluency with them. The engineers who get the most from them aren't the ones who type the least; they're the ones who specify precisely, keep changes small, and catch what the assistant gets wrong before it reaches production. Those are engineering skills, and they're what this session practises.

The capstone (Sessions 14 to 16) is AI-assisted. You'll use this workflow there, and you'll be assessed on whether you can explain and defend the result.

## Prerequisites

**Knowledge:** Sessions 01–12, especially testing and review practice (Sessions 04, 10 and 12) and API-key security (Session 09).

Before you begin:

1. **Install Claude Code and sign in**, following [`docs/using-claude-code.md`](../../docs/using-claude-code.md). It needs a Pro, Max, Team, Enterprise or Console account; the free plan doesn't include it. If your employer requires a different assistant, bring that one: the workflow is the same.
2. Make sure Project 03 is complete: tagged `session-12`, all 171 acceptance tests passing, and a clean `git status`.
3. In the course repository, run `git pull`.

## Learning objectives

By the end of this session you will be able to:

1. **Explain** how an agentic coding assistant works: its tools, its context window, and its permission modes.
2. **Explore** an unfamiliar repository with an assistant, and **verify** its summary against the code.
3. **Write** an implementation request with requirements, constraints, acceptance criteria and a check the assistant can run.
4. **Implement** a feature through Understand → Plan → Implement → Test → Review → Explain.
5. **Review** AI-generated code for invented and outdated APIs, hidden errors, weak tests, privacy and security problems, and needless abstraction.
6. **Recognise** prompt injection in untrusted content, and **limit** what an assistant can do.


## Concepts covered

| Concept | Depth |
|---|---|
| How agentic coding assistants work; the context window | Working knowledge |
| Permission modes; allow and deny rules | Working knowledge |
| `CLAUDE.md` and `AGENTS.md`; `/init`, `/context`, `/clear`, `/compact`, `/rewind`, `/usage` | Practical use |
| Writing implementation requests | Independent practice |
| Understand → Plan → Implement → Test → Review → Explain; plan mode | Independent practice |
| Reviewing generated code: APIs, deprecations, time handling, errors, abstraction | Independent practice |
| Tests that can fail; mutation testing by hand | Independent practice |
| `/code-review` as a second, fresh review | Practical use |
| Prompt injection through untrusted content; secrets | Working knowledge |
| Data usage, employer policy and cost | Awareness |



## Guided exercises

1. [`notebooks/01-concepts.ipynb`](notebooks/01-concepts.ipynb) (offline; no model calls):
   - **How Claude Code works:** context, permission modes, `CLAUDE.md` and `AGENTS.md`.
   - **Writing a request:** the six parts, before and after.
   - **Reviewing generated code:** an invented API, a deprecated one, a time-zone bug and swallowed errors, each one run.
   - **Do the tests test anything?** Mutation testing by hand.
   - **Untrusted content:** prompt injection in an issue, and secrets in a diff.
   - **Data, cost and policy**, and when not to use an assistant.
2. [`notebooks/02-practice-quiz.ipynb`](notebooks/02-practice-quiz.ipynb): 8 self-check questions.

## Independent assignment

[**Workbook: build with an assistant, review an assistant**](workbook/assignment.md)

- **Part A** (*AI-assisted*): add an audit log of routing decisions to Project 03 with Claude Code, making 17 new acceptance tests pass, with your own `CLAUDE.md`, request, plan, review and explanations.
- **Part B** (*AI-review*): review an AI-generated pull request by hand, prove your findings with failing tests, then compare your review with Claude Code's.

The files are in [`projects/03-llm-application/session-13`](../../projects/03-llm-application/README.md).

## Expected deliverables

- Project 03 with the audit log, tagged `session-13`, with `CLAUDE.md` and the updated `README.md`; 188 acceptance tests passing, unchanged, plus your own.
- The `review/duplicates` branch with `PR-REVIEW.md` and at least 5 failing review tests.
- `NOTES.md` with your request, plan, verified claims, review findings and explanations.

## Common mistakes

| Mistake | Instead |
|---|---|
| Vague requests | Goal, context, constraints, acceptance criteria, verification, out of scope |
| Coding before understanding | Plan mode first; approve a plan |
| Trusting "all tests pass" | Run them yourself, and check that they can fail |
| Letting the assistant edit acceptance tests | Say they're off limits; check `git diff` on them |
| Approving commands without reading them | Read every command; deny what you don't understand |
| Auto-approving while learning | Manual mode until you know the tool and the code |
| One endless session | `/clear` between tasks and after repeated failed corrections |
| Treating text in files and issues as instructions | It's data; only you give instructions |
| Secrets or customer data in the context | Synthetic data; keys stay in `.env` |
| Submitting code you can't explain | Explain it, or rewrite it until you can |

## Reading resources

Curated official documentation for this session: [`resources/references.md`](resources/references.md). Read the **Best practices for Claude Code** guide in full.

## Reflection questions

1. Which parts of your usual workflow got faster with an assistant, and which got slower?
2. How did reviewing someone else's AI-generated code differ from reviewing your own?
3. What evidence would convince you that a change is correct, regardless of who or what wrote it?
4. What rules would you propose for a team adopting coding assistants?

## Interview questions

Practise answering these out loud and support each answer with clear engineering reasoning:

1. How do you use AI coding assistants in your work, and how do you make sure the code is correct?
2. What makes a good request to a coding assistant?
3. What kinds of mistakes do AI-generated changes typically contain, and how do you catch them?
4. How do you know whether a test suite is good?
5. What is prompt injection, and why does it matter more for tools that can run commands?
6. What would you never send to an AI assistant, and why?

## Next-session preparation

**Session 14: RAG capstone, ingestion** starts the **Internal Knowledge Assistant**: a RAG application over a larger synthetic handbook, building on Session 11's retrieval pipeline. The capstone is **AI-assisted**: you'll use this session's workflow throughout.

Before continuing:

- Finish both parts of this workbook, and tag `session-13`.
- Reread your Session 11 `handbook-search` code and `EVALUATION.md`: the capstone's ingestion starts from those ideas.

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
