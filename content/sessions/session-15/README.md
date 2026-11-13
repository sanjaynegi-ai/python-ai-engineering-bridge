# Session 15: RAG Capstone, Application

**Phase 4: AI-Assisted Engineering and RAG Capstone**

## Session overview

Last week's index answers nothing yet. This session turns it into the **Internal Knowledge Assistant**: a question goes through retrieval, a numbered context, a language model that must answer only from those sources, and a citation check, and comes back as an answer with its sources, or as "I can't find this in the documentation".

The same service is then exposed three ways (a FastAPI endpoint, a Streamlit page and the CLI), and measured on 20 synthetic questions with known answers, including four the documentation doesn't cover. Everything runs and is tested without an API key; a live run with a real model is optional.

## Why this matters

A RAG assistant that answers fluently but can't show where an answer came from is a liability: an on-call engineer who follows an invented failover step causes the next incident. The engineering in this session (grounding, citation checks, explicit "not found", honest error handling, and measurement) is what separates a demo from a tool people can rely on at 3 a.m.

These are also the questions AI engineering interviews ask: how do you stop a model from making things up, how do you know retrieval works, what do you return when you don't know, and how do you test a system whose core is a paid, non-deterministic API?

## Prerequisites

**Knowledge:** Sessions 01–14, especially Session 07 (FastAPI), Session 09 (structured output, provider errors, fakes), Session 11 (retrieval, numbered contexts, thresholds) and Session 14 (your index).

**Setup:**

- Your `knowledge-assistant`, tagged `session-14`, with all 72 tests passing and an index built with the real embedder.
- Optional: your OpenAI key from Session 09, for one live run. No test needs it.

## Learning objectives

By the end of this session you will be able to:

1. **Implement** query → retrieve → build context → generate → cite, with "not found" at the retrieval and the model level.
2. **Validate** a model's citations, and refuse answers that can't be traced to a source.
3. **Expose** one service through FastAPI and a Streamlit UI, mapping each failure to the right status code or message.
4. **Evaluate** retrieval hit rate, answer rate, grounded rate and rejection rate, and **explain** each miss.
5. **Choose** a retrieval threshold from measurements, and **justify** it without tuning on your test set.


## Concepts covered

| Concept | Depth |
|---|---|
| Grounded generation with numbered sources | Guided integration |
| Structured output for answers (`answerable`, `answer`, `citations`) | Independent implementation |
| Two-level "not found"; choosing a threshold | Guided integration |
| Citation validation | Independent implementation |
| Thin adapters: FastAPI, Streamlit and the CLI over one service | Guided integration |
| Mapping domain errors to HTTP status codes | Independent implementation |
| Streamlit's rerun model, `st.cache_resource`, `AppTest` | Working knowledge |
| Retrieval evaluation and its four rates | Guided integration |



## Guided exercises

- **Notebook Part 1, Predict:** which threshold would you ship, from the measured scores?
- **Notebook Part 3, Explain and Challenge:** five replies; write the citation check before the workbook asks.
- **Notebook Part 4:** the error-mapping pattern on a parcel-tracking API. Which status for which error, and why is "not found" a 200?
- **Notebook Part 6, Explain:** an 80% answer rate with a 40% grounded rate. What's happening?

## Independent assignment

[`workbook/assignment.md`](workbook/assignment.md): **Capstone application.** Copy the Session 15 files over your project, add three dependencies, extend `ARCHITECTURE.md` (Independent), then implement `answering.py`, `api.py`, `ui.py` and `evaluation.py` against 64 new acceptance tests (AI-assisted), and write `EVALUATION.md` from your own measurements.

## Expected deliverables

- Your `knowledge-assistant` repository, tagged `session-15`, with all 136 acceptance tests and your own tests passing, and Ruff clean.
- `ARCHITECTURE.md` with an "Answering" section.
- `EVALUATION.md`: the offline evaluation, an explanation of every miss, and a threshold decision tested on six questions you wrote before looking at scores.

## Common mistakes

| Mistake | Consequence | Better |
|---|---|---|
| Calling the model when nothing was retrieved | Paying for a guess from general knowledge | "Not found" before generating |
| Parsing the answer text for "I don't know" | Breaks with every phrasing | An `answerable` field |
| Trusting citations | Invented sources make wrong answers look checked | Check every number; refuse untraceable answers |
| Renumbering returned sources | "[3]" in the text points to the wrong source | Keep original numbers |
| Logic in the API or UI | Three versions of the rules | One `Assistant.ask()`; adapters translate |
| 404 or 500 for "not found" | Clients treat a normal answer as an error | 200 with `found: false` |
| Building the assistant on every rerun | Seconds of delay per click | `@st.cache_resource` |
| Counting errors as rejections | An outage improves the score | Require "no error" for a correct rejection |
| Reporting a threshold tuned on the evaluation set | An optimistic number | Confirm on questions you didn't tune on |

## Reading resources

[`resources/references.md`](resources/references.md): OpenAI structured outputs; FastAPI errors and response models; uvicorn's `--factory`; Streamlit's execution model, caching, session state, configuration and `AppTest`.

## Reflection questions

1. What does a valid citation prove about an answer, and what doesn't it?
2. Where in your code is the decision "this question isn't answerable" made? Is it made in more than one place, and is that right?
3. Which of the four rates would you watch after a change to the prompt? To chunking? To the model?
4. What would your assistant do if a document contained instructions aimed at it?
5. Which part of this week's work was easiest to test, and which hardest? Why?

## Interview questions

1. "How do you prevent a RAG system from hallucinating, and how do you know it worked?"
2. "What should a RAG API return when the documents don't contain the answer? Why that status code?"
3. "How would you evaluate retrieval separately from generation?"
4. "Your rejection rate went up after a deployment. Is that good news?"
5. "How do you test code whose core dependency is a paid, non-deterministic LLM API?"
6. "When would you choose Streamlit for a UI, and when wouldn't you?"

## Next-session preparation

**Session 16: Capstone review and Python readiness** is the last session: integration testing and systematic debugging, logging, a focused presentation of your assistant's architecture and limitations, and the practical readiness assessment.

Before continuing:

- Finish this workbook, with all 136 tests passing, and tag `session-15`.
- Make sure `ARCHITECTURE.md` and `EVALUATION.md` are current: you'll present from them.
- Prepare a focused demonstration: one answered question, one "not found", and one design decision you'd defend.
- Revise the course's foundations (Sessions 02–08): the assessment covers Python itself, not only the capstone.

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
