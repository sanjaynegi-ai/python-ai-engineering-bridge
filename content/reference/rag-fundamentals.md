# RAG Fundamentals

Retrieval-augmented generation answers a question in two steps: **retrieve** the passages most relevant to it from your documents, then have a language model **answer using only those passages**, citing them. It's how you get answers grounded in documentation the model never saw. Session 11 builds each piece by hand; the capstone (Sessions 14 to 16) turns them into an application.

## The two pipelines

| Ingestion (ahead of time) | Answering (per question) |
|---|---|
| 1. **Load** files: Markdown as text, PDFs page by page | 1. **Embed** the question with the same model |
| 2. **Chunk** them into passages, keeping metadata (file, title, section, page) | 2. **Search** for the nearest chunks; keep those above a threshold |
| 3. **Embed** each chunk into a vector | 3. **Build a context**: number the chunks as sources |
| 4. **Store** vectors, text and metadata | 4. **Generate** an answer from the sources only, citing them |
| | 5. **Check** the citations, and return the sources |

## Retrieval, by hand

```python
import hashlib
import re

import numpy as np


def embed(texts: list[str], dimensions: int = 256) -> np.ndarray:
    """A toy word-hashing embedder: deterministic and free. Real models embed meaning."""
    vectors = np.zeros((len(texts), dimensions), dtype=np.float32)
    for row, text in enumerate(texts):
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            vectors[
                row, int(hashlib.md5(word.encode()).hexdigest(), 16) % dimensions
            ] += 1
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


chunks = [
    {
        "text": "Promote the replica db-03 with the promotion job.",
        "source": "runbooks/database-failover.md",
    },
    {
        "text": "Rotate API credentials every 90 days.",
        "source": "policies/api-credentials.md",
    },
    {
        "text": "Switch the office to the backup internet link.",
        "source": "runbooks/vpn-outage.md",
    },
]
vectors = embed([c["text"] for c in chunks])

question = "How do I promote the database replica?"
scores = vectors @ embed([question])[0]  # cosine similarity: the vectors have length 1
best_first = np.argsort(-scores)
hits = [(float(scores[i]), chunks[i]) for i in best_first[:2] if scores[i] >= 0.2]

context = "\n\n".join(
    f"[{n}] ({c['source']})\n{c['text']}" for n, (_, c) in enumerate(hits, 1)
)
print([round(score, 2) for score, _ in hits])
print(context)
```

It prints scores of 0.46 and 0.24. The VPN runbook is the second hit only because it shares words such as "the" and "with": a word-matching embedder can't tell relevance from coincidence. That's why real models embed meaning, and why a threshold, chosen for that model, decides what counts as found.

## Decisions that matter

| Decision | Guidance |
|---|---|
| **Chunk size** | A few hundred to about a thousand characters. Split at headings first, then by size, with some overlap. Measure before tuning: on a small, clean corpus, size often matters less than you'd think |
| **Metadata** | Keep the file, title, section and page with every chunk. Without them, you can't cite, filter or debug |
| **Embedding model** | Use the **same** model for documents and questions. A local model (fastembed, `BAAI/bge-small-en-v1.5`) is free; a hosted one (OpenAI `text-embedding-3-small`) costs a little per token. Changing models means re-embedding everything |
| **Similarity threshold** | Belongs to **one** model: scores aren't comparable across models. Choose it from measurements on questions with known answers, and confirm it on questions you didn't tune on |
| **Top k** | Three to five chunks is typical. More gives the model more context and more noise, and costs more tokens |
| **The prompt** | Your rules in the instructions; the numbered sources and the question as input. Tell the model to answer only from the sources, to cite them as `[n]`, and to say when they don't answer the question |

## Failure modes

| Symptom | Likely cause |
|---|---|
| The right document is never retrieved | A vocabulary gap ("resolve" in the question, "response target" in the policy), chunks that split the answer, or a missing file |
| Irrelevant answers to off-topic questions | The threshold is too low, or there's no "not found" path |
| Correct-sounding answers without sources | The model answered from general knowledge: no grounding instruction, or citations not checked |
| Old text in answers after a document changed | Ingestion added instead of replacing, or a cache in front of retrieval |
| Everything got worse after "a small change" | Mixed embedding models or chunk settings in one index |

## A vector store: Chroma (Session 11)

```python
import chromadb
from chromadb.config import Settings

# EphemeralClient keeps everything in memory; PersistentClient(path=...) writes to disk
client = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
collection = client.get_or_create_collection(
    "handbook", configuration={"hnsw": {"space": "cosine"}}, embedding_function=None
)
# Stable IDs (source and position); metadata values can't be None
collection.upsert(
    ids=["runbooks/vpn-outage.md#0"],
    embeddings=[[0.6, 0.8]],
    documents=["Switch the office to the backup internet link."],
    metadatas=[{"source": "runbooks/vpn-outage.md", "section": "Mitigate"}],
)
result = collection.query(query_embeddings=[[0.6, 0.8]], n_results=1)
similarity = 1 - result["distances"][0][0]  # Chroma returns cosine distance
print(result["ids"][0], round(similarity, 3))
collection.delete(where={"source": "runbooks/vpn-outage.md"})
print(collection.count())
```
<!-- release:7 -->

Behaviours of Chroma 1.5 that the capstone designs around (Session 14):

- `add` with an ID that already exists is **silently ignored**: edits never land. Replace a changed document's chunks instead.
- `upsert` overwrites, but leaves chunks beyond a shortened document's new length: delete those too.
- Metadata values can't be `None`: `add` raises, `upsert` drops the key. Leave `None` out, and read with `.get()`.
- Record how the index was built (embedding model, chunk settings) and refuse to mix them; re-ingest instead.
- Ingest incrementally: compare a content hash of each file with what the index recorded, and only re-embed what changed.
<!-- /release:7 -->
<!-- release:8 -->

## Measuring it (Session 15)

Keep a small set of questions with the files that answer them, plus questions the documents **don't** answer. Report four rates, never just one:

| Rate | Of which questions | Counts |
|---|---|---|
| Retrieval hit rate | answerable | an expected file was retrieved |
| Answer rate | answerable | an answer was given (found, no error) |
| Grounded rate | answerable | the answer cites an expected file |
| Rejection rate | unanswerable | the assistant said it can't find it (and didn't fail) |

Raising the threshold improves rejection and lowers the answer rate: report them together, look at **which** questions changed, and treat errors separately from "not found".
<!-- /release:8 -->

## Further reading

- [Chroma documentation](https://docs.trychroma.com/docs/overview/introduction).
- [fastembed](https://qdrant.github.io/fastembed/), the local embedding library the course uses.
- [OpenAI: embeddings](https://developers.openai.com/api/docs/guides/embeddings).
- [`llm-api-patterns.md`](llm-api-patterns.md) and [`langchain-langgraph.md`](langchain-langgraph.md).
