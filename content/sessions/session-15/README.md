# Session 15: RAG Capstone, Application

**Phase 4: AI-Assisted Engineering and RAG Capstone** · Weekend 8 · 2-hour live session

## 1. Session overview

Last week's index answers nothing yet. This session turns it into the **Internal Knowledge Assistant**: a question goes through retrieval, a numbered context, a language model that must answer only from those sources, and a citation check, and comes back as an answer with its sources, or as "I can't find this in the documentation".

The same service is then exposed three ways (a FastAPI endpoint, a Streamlit page and the CLI), and measured on 20 synthetic questions with known answers, including four the documentation doesn't cover. Everything runs and is tested without an API key; a live run with a real model is optional.

## 2. Why this matters

A RAG assistant that answers fluently but can't show where an answer came from is a liability: an on-call engineer who follows an invented failover step causes the next incident. The engineering in this session (grounding, citation checks, explicit "not found", honest error handling, and measurement) is what separates a demo from a tool people can rely on at 3 a.m.

These are also the questions AI engineering interviews ask: how do you stop a model from making things up, how do you know retrieval works, what do you return when you don't know, and how do you test a system whose core is a paid, non-deterministic API?

## 3. Prerequisites

**Knowledge:** Sessions 01–14, especially Session 07 (FastAPI), Session 09 (structured output, provider errors, fakes), Session 11 (retrieval, numbered contexts, thresholds) and Session 14 (your index).

**Setup:**

- Your `knowledge-assistant`, tagged `session-14`, with all 72 tests passing and an index built with the real embedder.
- Optional: your OpenAI key from Session 09, for one live run. No test needs it.

## 4. Learning objectives

By the end of this session you will be able to:

1. **Implement** query → retrieve → build context → generate → cite, with "not found" at the retrieval and the model level.
2. **Validate** a model's citations, and refuse answers that can't be traced to a source.
3. **Expose** one service through FastAPI and a Streamlit UI, mapping each failure to the right status code or message.
4. **Evaluate** retrieval hit rate, answer rate, grounded rate and rejection rate, and **explain** each miss.
5. **Choose** a retrieval threshold from measurements, and **justify** it without tuning on your test set.

## 5. Estimated time

| Activity | Time |
|---|---:|
| Live session | 2 hours |
| Concepts notebook (revision) | 45 minutes |
| Practice quiz | 30 minutes |
| Workbook assignment | 3 hours |

## 6. Concepts covered

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

### Live session plan

| Time | Activity |
|---|---|
| 0:00–0:15 | **Problem and intuition.** The fluent wrong answer. What grounding, citations and "not found" each prevent |
| 0:15–0:35 | **Demonstration.** The query-flow diagram. Notebook Part 1 (choosing a threshold from real scores) and Part 3 (five model replies: which would you show?) |
| 0:35–1:35 | **Guided build.** Milestone 1 (10 min), then Milestone 2 against its tests, then the API |
| 1:35–1:50 | **Debugging.** The outage that improved the rejection rate (quiz Q3); the Streamlit page that forgets its answer (quiz Q2) |
| 1:50–2:00 | **Recap and assignment briefing.** Milestones 4–6, and the threshold exercise |

## 7. Live demonstration

1. The reference assistant (not distributed) answers *"How do I promote the orders database replica?"* through `POST /ask`, then through the Streamlit page, with `runbooks/database-failover.md` as its source.
2. *"What will the weather be in Zurich tomorrow?"*: rejected by the threshold, without a model call.
3. The offline evaluation: 94% retrieval hit rate, 75% rejection rate, and the three questions it lists, investigated with `knowledge-assistant search`.
4. With a key, if the instructor has one: the same evaluation with a real model, and how the grounded and rejection rates change.

## 8. Guided exercises

- **Notebook Part 1, Predict:** which threshold would you ship, from the measured scores?
- **Notebook Part 3, Explain and Challenge:** five replies; write the citation check before the workbook asks.
- **Notebook Part 4:** the error-mapping pattern on a parcel-tracking API. Which status for which error, and why is "not found" a 200?
- **Notebook Part 6, Explain:** an 80% answer rate with a 40% grounded rate. What's happening?

## 9. Independent assignment

[`workbook/assignment.md`](workbook/assignment.md): **Capstone application.** Copy the Session 15 files over your project, add three dependencies, extend `ARCHITECTURE.md` (Independent), then implement `answering.py`, `api.py`, `ui.py` and `evaluation.py` against 64 new acceptance tests (AI-assisted), and write `EVALUATION.md` from your own measurements.

## 10. Expected deliverables

- Your `knowledge-assistant` repository, tagged `session-15`, with all 136 acceptance tests and your own tests passing, and Ruff clean.
- `ARCHITECTURE.md` with an "Answering" section.
- `EVALUATION.md`: the offline evaluation, an explanation of every miss, and a threshold decision tested on six questions you wrote before looking at scores.

## 11. Common mistakes

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

## 12. Reading resources

[`resources/references.md`](resources/references.md): OpenAI structured outputs; FastAPI errors and response models; uvicorn's `--factory`; Streamlit's execution model, caching, session state, configuration and `AppTest`.

## 13. Reflection questions

1. What does a valid citation prove about an answer, and what doesn't it?
2. Where in your code is the decision "this question isn't answerable" made? Is it made in more than one place, and is that right?
3. Which of the four rates would you watch after a change to the prompt? To chunking? To the model?
4. What would your assistant do if a document contained instructions aimed at it?
5. Which part of this week's work was easiest to test, and which hardest? Why?

## 14. Interview questions

1. "How do you prevent a RAG system from hallucinating, and how do you know it worked?"
2. "What should a RAG API return when the documents don't contain the answer? Why that status code?"
3. "How would you evaluate retrieval separately from generation?"
4. "Your rejection rate went up after a deployment. Is that good news?"
5. "How do you test code whose core dependency is a paid, non-deterministic LLM API?"
6. "When would you choose Streamlit for a UI, and when wouldn't you?"

## 15. Next-session preparation

**Session 16: Capstone review and Python readiness** is the last session: integration testing and debugging under time pressure, logging, a short presentation of your assistant's architecture and limitations, and the practical readiness assessment.

Before the session:

- Finish this workbook, with all 136 tests passing, and tag `session-15`.
- Make sure `ARCHITECTURE.md` and `EVALUATION.md` are current: you'll present from them.
- Prepare a five-minute demonstration: one answered question, one "not found", and one design decision you'd defend.
- Revise the course's foundations (Sessions 02–08): the assessment covers Python itself, not only the capstone.
