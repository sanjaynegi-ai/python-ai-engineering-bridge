# Session 12: Introduction to LangGraph

**Phase 3: Python for AI Applications** · Weekend 6 · 2-hour live session · **Project 03, stage 3: Milestone 3**

## 1. Session overview

An LLM call is one step. Applications around it have to **decide**: retry invalid output, fall back when the provider is down, ask a person when the answer is doubtful, and act only when it's safe. This session is about expressing those decisions as a workflow, first in plain Python, then as a **LangGraph** state graph: typed state, nodes, edges, conditional routing, reducers, streaming, recursion limits and, briefly, pausing for a person.

The workbook completes **Project 03**: a routing workflow that pages, queues or sends each triaged incident report for review, built twice, plain and as a graph, behind one interface and one set of contract tests. It ends with a measured recommendation, as in Session 10.

## 2. Why this matters

LangGraph is the most common way to build stateful LLM workflows and agents in Python, so you'll read and extend it in AI codebases. But a graph framework is also easy to adopt where a function would do. Experienced engineers are expected to tell the difference, and to keep business rules testable whichever they choose.

The patterns here (record what happened, route on it, limit every loop, fail loudly on configuration errors) apply to any workflow around a model, with or without a framework.

## 3. Prerequisites

**Knowledge:** Sessions 01–11. In particular, Session 09's `Triager` interface and error classes, Session 10's contract tests and comparison, and Session 04's testing practice.

**Before the session:**

1. In the course repository, run `git pull` and `uv sync`. LangGraph is already in the notebook kernel (the `ai` group, since Session 10).
2. Finish the Session 10 workbook, tagged `session-10`, with all 119 acceptance tests passing. Session 12 builds directly on it.
3. Think of a workflow you've built or maintained with retries, fallbacks or approvals. How was its control flow expressed: in code, configuration, or a workflow engine?

## 4. Learning objectives

By the end of this session you will be able to:

1. **Explain** when a stateful graph is justified, and when plain Python is enough.
2. **Define** typed graph state with a reducer, nodes that return updates, and fixed and conditional edges.
3. **Implement** conditional routing with a retry loop and a fallback, and **derive** a recursion limit for it.
4. **Run, stream and debug** a graph step by step, and **interpret** its errors.
5. **Test** a graph through its routing functions, its runs, its structure and a contract with a plain version.
6. **Assess** LangGraph against plain Python for the same workflow, and **recommend** one.

## 5. Estimated time

| Activity | Time |
|---|---:|
| Live session | 2 hours |
| Concepts notebook (revision on your own) | 60 minutes |
| Practice quiz | 30 minutes |
| Workbook assignment (Project 03, stage 3) | 2–2.5 hours |

## 6. Concepts covered

| Concept | Depth |
|---|---|
| Plain Python or a graph: the decision | Independent judgment |
| `StateGraph`, `TypedDict` state, nodes returning updates | Guided integration |
| Reducers (`Annotated[..., operator.add]`) | Guided integration |
| Fixed and conditional edges; declared destinations; `START` and `END` | Guided integration |
| Loops with a counter; `recursion_limit` and `GraphRecursionError` | Guided integration |
| `invoke` and `stream` (`updates`, `values`); `draw_mermaid` | Working knowledge |
| Error propagation from nodes | Working knowledge |
| `interrupt`, checkpointers and resuming | Awareness |
| Testing graphs: routing functions, runs, structure, contracts | Guided integration |
| Agents, multi-agent systems, parallel branches | Not covered: named as future topics |

### Live session plan

| Segment | Time | What happens |
|---|---:|---|
| Problem and intuition | 20 min | "After triage, what happens?" The alert workflow in plain Python; when the control flow becomes the hard part |
| Visual explanation and demo | 25 min | State, nodes, edges and reducers; conditional routing; the workflow as a graph, drawn and streamed |
| Guided coding | 40 min | Together: the business rules and the start of `build_workflow`, until the structure tests pass |
| Debugging challenge | 20 min | A list that keeps only its last item, a route that silently ends the run, and a loop that would make 10,007 calls |
| Recap and assignment briefing | 15 min | Key takeaways; the comparison criteria; the Milestone 3 checkpoint |

## 7. Live demonstration

The instructor will:

1. Write the alert-escalation workflow as a plain function, and list the requirements that would make it hard.
2. Build a graph step by step: state, one node, two nodes, a reducer.
3. Add conditional edges, and show what an undeclared destination does to the drawing and to a misspelled route.
4. Run the full workflow, draw it with `draw_mermaid()`, and stream each step.
5. Trigger a runaway loop, count the calls, then stop it with a recursion limit derived from the longest path.
6. Pause a run with `interrupt`, inspect it, and resume it with `Command(resume=...)`.
7. Test the graph four ways, including a contract with the plain version.

## 8. Guided exercises

1. [`notebooks/01-concepts.ipynb`](notebooks/01-concepts.ipynb) (offline; no LLM calls):
   - **Plain Python first:** the baseline, and the diagram comparing a pipeline with a workflow.
   - **State, nodes and edges:** the smallest graph.
   - **Reducers:** replacing, appending, and two silent mistakes.
   - **Conditional edges:** declared destinations, and misspelled routes.
   - **The alert workflow as a graph**, drawn as Mermaid.
   - **Running and debugging:** streaming, errors from nodes, loops and recursion limits.
   - **Pausing for a person:** `interrupt` and a checkpointer.
   - **Testing a graph**, and **the workflow you'll build**, with its diagram.
   - **Plain Python or LangGraph?** The trade-offs.
2. [`notebooks/02-practice-quiz.ipynb`](notebooks/02-practice-quiz.ipynb): 9 self-check questions.

## 9. Independent assignment

[**Workbook: route the triage, twice**](workbook/assignment.md) (*Independent*: no AI coding assistant)

Implement the routing workflow in plain Python and as a LangGraph graph, make 52 new acceptance tests pass (most of them a contract run against both), then measure the two and recommend one. The new files are in [`projects/03-llm-application/session-12`](../../projects/03-llm-application/README.md). This completes Project 03 (Milestone 3).

## 10. Expected deliverables

- The `incident-triage` project with `PlainRouter` and `GraphRouter`, tagged `session-12`.
- `uv run pytest` passing with no API key: 171 acceptance tests, unchanged, plus your own.
- The Session 12 section of `COMPARISON.md`, `NOTES.md`, and the updated project `README.md`.

## 11. Common mistakes

| Mistake | Instead |
|---|---|
| A graph for a straight pipeline | Plain functions until the control flow is the hard part |
| Conditional edges without declared destinations | A list, a mapping, or a `Literal` return type |
| A list key without a reducer | `Annotated[list[...], operator.add]` |
| Misspelled keys in an update | Test node outputs; they're dropped silently |
| Mutating the state in a node | Return an update; treat the state as read-only |
| No recursion limit on a loop | A counter in the state, and a limit derived from the longest path |
| `except Exception` in a node | Catch what the workflow handles; let configuration errors and bugs propagate |
| Business rules inside nodes | Plain functions both versions can share and test |
| Side effects before `interrupt` | They run again on resume: move them to an earlier node |

## 12. Reading resources

Curated official documentation for this session: [`resources/references.md`](resources/references.md).

## 13. Reflection questions

1. Where in your current or past systems would an explicit workflow graph have helped, and where would it have been overhead?
2. How do you decide whether logic belongs in a node, a routing function, or a separate business-rule function?
3. Which failures should stop a whole run, and which should only change one item's route? How did you decide in this project?
4. What would you need before letting a workflow act on its own decisions, such as paging someone at 3 a.m.?

## 14. Interview questions

Practise answering these out loud, in two minutes or less each:

1. What is LangGraph, and when would you not use it?
2. Explain state, nodes, edges and reducers in LangGraph.
3. How do conditional edges work, and how do you make them safe?
4. How do you stop an LLM workflow from looping forever, or from running up a large bill?
5. How would you add a human approval step to an automated workflow?
6. How do you test a workflow that calls an LLM?
7. Workflow or agent: what's the difference, and how do you choose?

## 15. Next-session preparation

**Session 13: Claude Code for professional engineering** moves from building AI features to building **with** AI: using an AI coding assistant to explore a repository, plan, implement, test and review a change, while keeping engineering ownership. The live demonstration works on Project 03.

Before the session:

- Finish this workbook, tag `session-12`, and make sure Project 03 is complete: this is the Milestone 3 checkpoint.
- Install Claude Code by following [`docs/using-claude-code.md`](../../docs/using-claude-code.md), and sign in. Don't run it on Project 03 yet.
