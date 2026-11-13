# Session 12 Assignment: Route the Triage, Twice

**Type:** Independent. Complete this without an AI coding assistant; Session 13 covers AI-assisted work.
**Builds on:** [`01-concepts.ipynb`](../notebooks/01-concepts.ipynb), and your Session 10 work on Project 03
**Project:** **Project 03: LLM-Powered Application** (`incident-triage`), stage 3 of 3. This completes **Milestone 3**.

---

## Business scenario

`incident-triage` now produces a validated triage for every report, through the SDK or LangChain. The on-call team wants the next step automated: **what happens to each report.**

- A P1 should **page** the owning team's on-call engineer.
- Anything less urgent should go to the owning team's **queue**.
- Anything doubtful should go to the triage desk for a person to **review**: no owning team, a P1 that doesn't say what's broken, a security incident rated as minor, or a high priority that came from the keyword rules rather than the model.

And the LLM's failures need handling: invalid output deserves one more try, an unavailable provider shouldn't stop the run (fall back to the keyword rules), and a refusal should go to a person.

The architect wants to know whether LangGraph is worth adopting for workflows like this. As in Session 10, you'll settle it with evidence: build the workflow in plain Python and as a LangGraph graph, prove that both behave identically with the same tests, and recommend one.

## Learning objectives

By completing this assignment you will:

- **Implement** business rules as plain functions that any workflow can share.
- **Implement** a workflow with a retry loop, a fallback and several destinations in plain Python.
- **Define** typed graph state with a reducer, nodes that return updates, and declared conditional edges.
- **Derive** and **test** a recursion limit from the workflow's longest path.
- **Debug** a graph with streaming, and **interpret** LangGraph's errors.
- **Assess** LangGraph against plain Python for the same workflow, with measurements.

## Prerequisites

- **Your Session 10 project** (`incident-triage`, tagged `session-10`) with all 119 acceptance tests passing, and your `COMPARISON.md`.
- The Session 12 concepts notebook.
- **No API key** is needed. **Optional:** an OpenAI API key, for a live run in Milestone 6.

---

## Project setup

Before adding anything, record your environment's package count again, for the comparison:

```bash
cd ~/skillup/incident-triage
uv pip list | wc -l              # PowerShell: (uv pip list | Measure-Object -Line).Lines
```

Copy the contents of the course repository's `projects/03-llm-application/session-12/` over your project, and add LangGraph:

```bash
# macOS / Linux / Git Bash
cp -r ~/python-ai-engineering-bridge/projects/03-llm-application/session-12/. ~/skillup/incident-triage/

# PowerShell
Copy-Item -Recurse -Force ~\python-ai-engineering-bridge\projects\03-llm-application\session-12\* ~\skillup\incident-triage\
```

```bash
uv add langgraph
git add .
git commit -m "Session 12 starter files"
git tag session-12-start
uv run pytest
```

| File | Status |
|---|---|
| `src/incident_triage/routing.py` | The contract (`Dispatch`, `Routing`, `RoutingRun`, `Router`) and `route_all` provided; the rules and `PlainRouter` are stubs. Yours |
| `src/incident_triage/workflow.py` | Stubs: `TriageState`, `build_workflow`, `GraphRouter`. Yours |
| `src/incident_triage/cli.py` | Updated, provided: a new `--route plain\|graph` option |
| `tests/acceptance/test_routing.py` | Provided. Don't edit |

Your earlier 119 acceptance tests still pass. Of the 52 new ones, 1 passes now (the CLI fails fast without a key before any routing) and the rest fail until you implement the stubs.

Read `test_routing.py` before you start. Most of it is a **contract**: each test runs twice, as `[plain]` and `[graph]`, with scripted triagers that return a triage or raise one of your Session 09 errors in a set order. No test calls an API.

---

## Requirements

| # | Requirement |
|---|---|
| R1 | All 171 acceptance tests pass, unchanged: 119 from Sessions 09–10 and 52 in `test_routing.py`. |
| R2 | `PlainRouter` and `GraphRouter` satisfy the `Router` protocol and pass the same contract tests. |
| R3 | The business rules are written once, in `review_reasons`, and both routers use them. |
| R4 | The graph has six nodes (`triage`, `fallback`, `check`, `page`, `queue`, `review`); every conditional edge declares its destinations; nodes return only the keys they change and never mutate the state. |
| R5 | `GraphRouter` passes a recursion limit derived from `max_attempts`: the smallest that lets the longest path finish. |
| R6 | LangGraph is imported only in `workflow.py`. |
| R7 | A new section in `COMPARISON.md` compares the two routers and recommends one (Milestone 7). |
| R8 | At least **6** test cases of your own in `tests/unit/`. |
| R9 | `uv run ruff check .` and `uv run ruff format --check .` pass. |

---

## Implementation milestones

### Milestone 1: Predict

Read the docstrings in `routing.py` and the diagram in Part 9 of the concepts notebook. In `NOTES.md`, write down the `path` you expect for each of these, then check them against `test_routing.py`:

1. The model returns a P2 for the network team.
2. The model returns invalid output twice (with the default `max_attempts=2`), and the keyword rules then give a P1.
3. The provider times out.
4. The model refuses.

Also predict: which version, plain or graph, will be longer, and by roughly how much?

### Milestone 2: The business rules

Implement `review_reasons` and `dispatch_for` in `routing.py`. They're plain functions of a `Triage`: no workflow, no LLM.

```bash
uv run pytest tests/acceptance/test_routing.py -k "rule and not review"
```

### Milestone 3: `PlainRouter`

Implement `PlainRouter.__init__` and `route` following the docstring. Design questions to settle first, in `NOTES.md`:

- `LLMConfigurationError` is a subclass of `TriageError`. What does that mean for the order of your `except` clauses?
- After a retry succeeds, `Routing.error` still holds the first attempt's error. Why might that be useful to the on-call team?
- Where does the loop counter live, and how do you make sure nothing is left over when the same router routes a second report?

```bash
uv run pytest tests/acceptance/test_routing.py -k plain
```

### Milestone 4: The graph

In `workflow.py`, define `TriageState` and implement `build_workflow`.

- **State:** the docstring names three keys the tests rely on (`report`, `attempts`, `path`). Add what your nodes need to pass information to the routing functions. `path` needs a **reducer** so that each node can append its own name.
- **Nodes** do one thing each and return an update. In particular, `triage` calls the triager and **records** what happened; it doesn't decide where to go next.
- **Routing functions** decide. Keep them small, and reuse `review_reasons` and `dispatch_for`.
- **Dependencies** (the two triagers, `max_attempts`) reach the nodes through the closure, as in the concepts notebook.
- **Declare** the destinations of every conditional edge.

```bash
uv run pytest tests/acceptance/test_routing.py -k "nodes or declares or streaming"
```

Then print the graph and check it against the diagram before going on:

```bash
uv run python -c "from incident_triage.workflow import build_workflow; from incident_triage.offline import KeywordTriager; print(build_workflow(KeywordTriager(), KeywordTriager()).get_graph().draw_mermaid())"
```

Paste the output into `NOTES.md`. If your editor or Git host renders Mermaid, look at the picture too.

### Milestone 5: `GraphRouter`

Implement `GraphRouter`: build the graph once in `__init__`, then in `route`, invoke it with the starting state and `{"recursion_limit": self.recursion_limit}`, and turn the final state into a `Routing`.

Work out the recursion limit **from the longest possible path**, not by trial and error, and write your reasoning in `NOTES.md`. The concepts notebook (Part 6) shows how the limit relates to the number of nodes that run.

```bash
uv run pytest tests/acceptance/test_routing.py
uv run pytest
```

### Milestone 6: Run it

1. Route the sample reports with both workflows, and compare the outputs:

   ```bash
   uv run incident-triage data/reports.jsonl --offline --route plain --out out/plain.json
   uv run incident-triage data/reports.jsonl --offline --route graph --out out/graph.json
   git diff --no-index out/plain.json out/graph.json
   ```

   The last command should print nothing.
2. Look at which reports went to review, and why. The keyword rules queue the phishing report (`RPT-1011`) as ordinary IT support. Is that a problem with the routing, or with its input? What would the LLM triage do differently?
3. Stream one report through the graph, and record in `NOTES.md` what each node returned. Use a scripted triager like the tests', or the `KeywordTriager`:

   ```python
   for update in graph.stream(
       {"report": report, "attempts": 0, "path": []}, stream_mode="updates"
   ):
       print(update)
   ```

4. **Optional, with an API key:** route the sample reports with the LLM (`--route graph`, without `--offline`). Which reports does the model route differently from the keyword rules? Check `RPT-1010`, the prompt-injection attempt.

### Milestone 7: Compare

Add a section **"Session 12: plain Python or LangGraph?"** to `COMPARISON.md`, with these measurements:

1. **Code size.** Non-blank, non-comment lines of `PlainRouter` and of `workflow.py` (adapt the Session 10 command).
2. **Dependencies.** The package count now, against the one you recorded at setup. Which packages did `langgraph` bring?
3. **Debugging.** Break the same thing in both versions on purpose (for example, make an unavailable provider retry), run `uv run pytest -x --tb=long -k unavailable`, and compare the two tracebacks. Undo the change.
4. **Testing.** Which tests needed nothing graph-specific? What did the graph need that the plain version didn't?
5. **What the graph gives you** that this workflow uses today, and what it would give if the requirements grew: pausing for a person, resuming, streaming progress.

End with **one paragraph of recommendation** for this workflow, as you'd present it to the architect, and say what would change your mind. Either answer can be right; the reasons are what's assessed.

### Milestone 8: Your own tests

Create at least **6** test cases in `tests/unit/`. Ideas:

- Each routing function on its own, called with hand-made state dicts.
- A refusal **after** an invalid attempt: what's the path, and which error is kept?
- `max_attempts=1` with an unavailable provider and with invalid output: same path or not?
- The graph's final state contains no keys that a node didn't set (for example, no `dispatch` before an action node runs: stream with `"values"`).
- `route_all` with a configuration error on the third report: the first two aren't returned, and the error reaches the caller.
- A misspelled destination in a routing function fails loudly (build a small graph in the test).

Prove that two of your tests can fail, as before.

### Milestone 9: Quality gate and Milestone 3 checkpoint

Update your project's `README.md`: add Session 12 to the stages table, the `--route` option to the usage section, and `routing.py` and `workflow.py` to the layout. Then:

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
git add .
git commit -m "Session 12: routing workflow, plain Python and LangGraph"
git tag session-12
```

This completes **Project 03**. The checkpoint review looks at the whole project: Sessions 09, 10 and 12.

---

## Acceptance criteria

| Check | Expected result |
|---|---|
| `uv run pytest tests/acceptance` | `171 passed`, with no API key and no network |
| `uv run pytest tests/unit` | Your earlier tests plus at least 6 new ones pass |
| `git grep -n -E "langgraph" -- src` | Matches only in `src/incident_triage/workflow.py` |
| `uv run incident-triage data/reports.jsonl --offline --route graph` | Every report paged, queued or sent for review; a summary line; exit code `0` |
| `git diff --no-index out/plain.json out/graph.json` after Milestone 6 | No output |
| `uv run incident-triage data/reports.jsonl --route graph` without a key | A one-line error naming `OPENAI_API_KEY`; exit code `2` |
| `git diff session-12-start -- tests/acceptance tests/conftest.py` | No output |
| `uv run ruff check .` and `uv run ruff format --check .` | Both pass |
| `COMPARISON.md` | The Session 12 section, with five measurements and a recommendation |
| `NOTES.md` | Predictions, design answers, the Mermaid output, a streamed run, the recursion-limit reasoning, and the reflection |

## Debugging guidance

| You see | Where to look |
|---|---|
| `test_a_configuration_error_stops_everything` fails: the fallback was called | `except TriageError` comes before `except LLMConfigurationError`, and catches it first: it's a subclass. |
| `KeyError: 'attempts'` inside your `triage` node | The key isn't set until something writes it. Default it in the node, or start the graph with it. |
| `path` holds only the last node's name | `path` has no reducer: each update replaces it. |
| `test_the_graph_declares_every_route` lists missing edges | A conditional edge without declared destinations. Pass a list, or give the routing function a `Literal` return type. |
| `KeyError` whose value looks like a node name | A routing function returned a name that isn't a node. Check the spelling against `add_node`. |
| `KeyError: 'dispatch'` in `GraphRouter.route`, and a log line saying "wrote to unknown channel ... ignoring it" | An undeclared route returned an unknown name, and the run quietly ended early. Declare the destinations. |
| `GraphRecursionError` in `test_max_attempts[graph-3]` | Your limit doesn't grow with `max_attempts`, or is one too small. Count the nodes on the longest path. |
| `test_the_router_can_be_reused` fails for one version | State left over from the first report: an attribute on `self`, a module-level list, or attempts not reset. |
| `test_invalid_output_is_retried[graph]` has `error` `None` | Your `triage` node clears the error when a retry succeeds. The contract keeps the last error. |
| `test_streaming_shows_each_step_and_what_it_changed` finds `dispatch` in the first update | A node returned the whole state instead of only what it changed. |
| `InvalidUpdateError: Expected dict` | A node returned something other than a dict, such as a `Triage` or a string. |

## Extension challenges (optional)

1. **Retry with feedback.** On invalid output, send the validation error back to the model in the retry ("your previous answer was invalid because ..."). Which interface has to change? Does it fit better in the plain version or the graph?
2. **Approval before paging.** Add an `approve` node before `page` that calls `interrupt(...)`, compile with `InMemorySaver`, and resume with `Command(resume=...)`. Write a test that pauses, resumes with "no", and ends in review. What would the plain-Python version need to do the same?
3. **A routing log.** Log each node's update with `logging` as the graph streams, without report text, so an on-call engineer can see why a report was routed. Test that no report text appears in the logs.
4. **Plug into Project 02.** Expose `route` as `POST /reports/route` in your Session 08 API, behind the `Router` protocol, with a fake router in the API tests.

## Reflection

Answer briefly in `NOTES.md`:

1. How close were your Milestone 1 predictions, especially the code-size estimate?
2. Which bug did the contract tests catch in one version but not the other?
3. Where would you put the next business rule, and how many files would change in each version?
4. Compare LangGraph with a state-machine or workflow tool you've used (Spring Statemachine, Stateless, XState, Step Functions, Temporal). What does it make easier, and what does it leave to you?

## Deliverables

Submit **one** of the following, as your course instructions specify:

- a link to a Git repository containing the project, with the `session-12` tag (push only to a repository you own; keep it private if you prefer), **or**
- a `.zip` of the project folder **without** `.venv/`, `out/` and `.env`.

The submission must include:

- [ ] `review_reasons`, `dispatch_for`, `PlainRouter`, `TriageState`, `build_workflow` and `GraphRouter` implemented
- [ ] `tests/acceptance/` and `tests/conftest.py` unchanged, and your `tests/unit/` with at least 6 new test cases
- [ ] `COMPARISON.md` with the Session 12 section and your recommendation
- [ ] `NOTES.md` with your predictions, design answers, the Mermaid output, a streamed run and the reflection
- [ ] The updated project `README.md`
- [ ] All acceptance criteria passing

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
