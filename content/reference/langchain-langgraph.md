# LangChain and LangGraph

LangChain gives you common interfaces over models, prompts and parsers, composed into pipelines. LangGraph builds stateful workflows as graphs: nodes that update shared state, with conditional routing between them. Both are useful, and neither is required: a direct SDK call (Session 09) and plain Python control flow are often clearer. Session 10 compares the two approaches on the same feature; Session 12 does the same for workflows.

The course's versions: `langchain-core` 1.6–1.7, `langchain-openai` 1.7, `langgraph` 1.2. These libraries change quickly: check the documentation for your version before copying older examples.

## When to use which

| You need | Start with |
|---|---|
| One model call with structured output | The provider's SDK directly |
| To swap providers often, or use LangChain's integrations (loaders, retrievers, tools) | LangChain |
| A fixed sequence: prompt → model → parse | Either; plain Python is shortest |
| Loops, retries, branches, human approval, resuming after a failure | LangGraph, or a small state machine in plain Python if it stays small |
| Multi-agent orchestration | Out of scope for this course |

## LangChain: composing a chain

```python
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You triage incident reports for the IT operations team."),
        ("human", "Report: {report}"),
    ]
)
# A test double that replies with a fixed answer
model = FakeListChatModel(responses=["P2, network: the Berlin VPN drops."])
# LCEL: each step's output is the next step's input
chain = prompt | model | StrOutputParser()

print(chain.invoke({"report": "VPN keeps dropping in Berlin."}))
# Every runnable also has batch and stream
print(chain.batch([{"report": "a"}, {"report": "b"}]))
```

- Every piece is a **Runnable** with `invoke`, `batch`, `stream` and their async versions.
- `ChatPromptTemplate` fills `{placeholders}`; the human message carries untrusted text, the system message your rules.
- The fake model makes the chain testable without a provider. With a real one, replace it with `ChatOpenAI(model="gpt-5.6-terra")` from `langchain_openai`.

## LangChain: structured output

```python
import json

import httpx2
from langchain_openai import ChatOpenAI
from pydantic import BaseModel


class Triage(BaseModel):
    priority: str
    team: str


def fake_responses_api(request: httpx2.Request) -> httpx2.Response:
    """Replies like OpenAI's Responses API, so this runs without a key."""
    text = json.dumps({"priority": "P2", "team": "network"})
    return httpx2.Response(
        200,
        json={
            "id": "resp_1",
            "object": "response",
            "created_at": 1761120000,
            "model": "gpt-5.6-terra",
            "status": "completed",
            "error": None,
            "incomplete_details": None,
            "instructions": None,
            "metadata": {},
            "parallel_tool_calls": True,
            "temperature": None,
            "tool_choice": "auto",
            "tools": [],
            "top_p": None,
            "output": [
                {
                    "type": "message",
                    "id": "msg_1",
                    "role": "assistant",
                    "status": "completed",
                    "content": [
                        {"type": "output_text", "text": text, "annotations": []}
                    ],
                }
            ],
            "usage": {
                "input_tokens": 50,
                "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
                "output_tokens": 10,
                "output_tokens_details": {"reasoning_tokens": 0},
                "total_tokens": 60,
            },
        },
    )


model = ChatOpenAI(
    model="gpt-5.6-terra",  # always name the model: ChatOpenAI's default is an old one
    api_key="not-a-real-key",
    use_responses_api=True,
    max_retries=2,
    timeout=30,
    http_client=httpx2.Client(transport=httpx2.MockTransport(fake_responses_api)),
)
structured = model.with_structured_output(Triage)
print(structured.invoke("VPN keeps dropping in Berlin."))
```

Things the course measured in these versions (Session 10):

- With `include_raw=True`, a **refusal** arrives as a parsing error, but invalid or truncated output still **raises** `pydantic.ValidationError` from inside the SDK.
- LangChain's exception mapping doesn't cover 408 or 409: those arrive as `openai.APIStatusError` subclasses.
- `with_retry()` on top of the SDK's own `max_retries` multiplies requests (3 × 3 = 9).
<!-- release:6 -->

## LangGraph: a validate-and-route workflow (Session 12)

```python
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict, total=False):
    report: str
    priority: str
    attempts: int
    route: str


def triage(state: State) -> State:
    # in a real workflow: a model call. Nodes return only the keys they change.
    attempts = state.get("attempts", 0) + 1
    # The first answer is invalid, to show a retry
    priority = "P9" if attempts == 1 else "P1"
    return {"priority": priority, "attempts": attempts}


def choose(state: State) -> Literal["retry", "page", "review"]:
    if state["priority"] not in {"P1", "P2", "P3", "P4"}:
        return "retry" if state["attempts"] < 2 else "review"
    return "page" if state["priority"] == "P1" else "review"


def page(state: State) -> State:
    return {"route": "paged the on-call engineer"}


def review(state: State) -> State:
    return {"route": "sent to human review"}


graph = StateGraph(State)
graph.add_node("triage", triage)
graph.add_node("page", page)
graph.add_node("review", review)
graph.add_edge(START, "triage")
graph.add_conditional_edges(
    "triage", choose, {"retry": "triage", "page": "page", "review": "review"}
)
graph.add_edge("page", END)
graph.add_edge("review", END)
app = graph.compile()

result = app.invoke(
    {"report": "Checkout is down for everyone."}, {"recursion_limit": 10}
)
print(result["attempts"], result["priority"], result["route"])
```

Things the course measured in LangGraph 1.2.16 (Session 12):

- **Declare the destinations** of conditional edges (a mapping, or a `Literal` return type). Without them, a router returning an unknown name only logs a warning and ends the run; with them, it raises `KeyError`.
- A node's update with a key that isn't in the state schema is **silently ignored**.
- The default `recursion_limit` was 10,007 steps, not the 25 of older tutorials. Pass your own: a path through n nodes needs at least n + 1.
- Don't mutate the state you're given inside a node: return the changes.
- Debug with `app.stream(inputs, stream_mode="updates")` (one item per node) and `app.get_graph().draw_mermaid()`.
<!-- /release:6 -->

## Further reading

- [LangChain overview](https://docs.langchain.com/oss/python/langchain/overview) and [structured output](https://docs.langchain.com/oss/python/langchain/structured-output).
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) and [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api).
- [`llm-api-patterns.md`](llm-api-patterns.md): the direct approach these build on.
