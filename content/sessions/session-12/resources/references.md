# Session 12: References

Official documentation first. Each link says *why* it's worth your time, so you can pick what you need instead of reading everything. LangGraph changes quickly: check what you read against the version in your lockfile, and measure defaults yourself (the recursion limit is an example: see the concepts notebook, Part 6).

## Deciding whether you need a graph

| Resource | Read it for |
|---|---|
| [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | The distinction between workflows and agents, and the advice to start with the simplest solution and add complexity only when it's needed |
| [LangGraph: Workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents) | Common workflow patterns (chaining, routing, parallel steps, evaluator loops) shown in LangGraph |
| [LangGraph: Thinking in LangGraph](https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph) | How to break a process into nodes and decide what goes into the state |

## The graph API

| Resource | Read it for |
|---|---|
| [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) | What LangGraph is for, and how it relates to LangChain |
| [Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api) | State, reducers, nodes, edges, `START` and `END`, and the recursion limit, in depth |
| [Use the graph API](https://docs.langchain.com/oss/python/langgraph/use-graph-api) | How-to examples: conditional edges, loops, controlling the number of steps |
| [Streaming](https://docs.langchain.com/oss/python/langgraph/streaming) | The stream modes (`updates`, `values` and others), for debugging and progress |
| [Test](https://docs.langchain.com/oss/python/langgraph/test) | LangGraph's own advice on testing graphs, nodes and partial runs |
| [`langgraph` API reference: graphs](https://reference.langchain.com/python/langgraph/graphs) | `StateGraph` and `CompiledStateGraph`: every method and parameter |

## Errors

| Resource | Read it for |
|---|---|
| [`GRAPH_RECURSION_LIMIT`](https://docs.langchain.com/oss/python/langgraph/errors/GRAPH_RECURSION_LIMIT) | What `GraphRecursionError` means, and how to tell a real loop from a long but legitimate path |
| [`INVALID_GRAPH_NODE_RETURN_VALUE`](https://docs.langchain.com/oss/python/langgraph/errors/INVALID_GRAPH_NODE_RETURN_VALUE) | The `InvalidUpdateError` you get when a node returns something other than a dict |

## Pausing, persistence and resuming

| Resource | Read it for |
|---|---|
| [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) | `interrupt` and `Command(resume=...)` for human-in-the-loop steps, including why code before `interrupt` runs again |
| [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) | Checkpointers, threads and saved state: what you need before using interrupts in production |

## Python and tools

| Resource | Read it for |
|---|---|
| [`typing.TypedDict`](https://docs.python.org/3/library/typing.html#typing.TypedDict) | The state schema: `total=False`, and how type checkers treat optional keys |
| [`typing.Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated) | The syntax LangGraph uses to attach a reducer to a key |
| [Mermaid](https://mermaid.js.org/) | The diagram language `draw_mermaid()` produces, and where it renders |

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
