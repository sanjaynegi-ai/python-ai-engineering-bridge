# Session 11: References

Official documentation first. Each link says *why* it's worth your time, so you can pick what you need instead of reading everything.

## Retrieval-augmented generation

| Resource | Read it for |
|---|---|
| [Lewis et al. (2020): Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) | The paper that named RAG. The introduction and the figure are enough to see the original idea |
| [Anthropic: Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) | Why chunks lose context, and how adding context to each chunk (as `embedding_text` adds the title and section) and combining embeddings with keyword search improve retrieval, with measurements |
| [LangChain: Retrieval](https://docs.langchain.com/oss/python/langchain/retrieval) | LangChain's vocabulary for the same pipeline: loaders, splitters, embedding models, vector stores, retrievers |
| [LangChain: Build a RAG agent](https://docs.langchain.com/oss/python/langchain/rag) | The same steps with LangChain components, for comparison with the hand-built version |
| [OWASP: LLM01 Prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | Indirect prompt injection through retrieved documents, and layered mitigations |

## Loading and chunking

| Resource | Read it for |
|---|---|
| [pypdf: Extract text from a PDF](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) | `extract_text`, and why PDF text extraction is imperfect (layout, scanned pages, ligatures) |
| [pypdf: Metadata](https://pypdf.readthedocs.io/en/stable/user/metadata.html) | Reading a PDF's title, and why `metadata` can be `None` |
| [LangChain: Text splitters](https://docs.langchain.com/oss/python/integrations/splitters) | The library splitters from Part 3, including splitting by Markdown headers |
| [`langchain-text-splitters` API reference](https://reference.langchain.com/python/langchain-text-splitters) | Parameters of `RecursiveCharacterTextSplitter` and the other splitters |

## Embeddings

| Resource | Read it for |
|---|---|
| [FastEmbed documentation](https://qdrant.github.io/fastembed/) | The local embedding library used in this session: `TextEmbedding`, caching and batching |
| [FastEmbed: Supported models](https://qdrant.github.io/fastembed/examples/Supported_Models/) | Other models you can try, with their dimensions and sizes |
| [BAAI/bge-small-en-v1.5 model card](https://huggingface.co/BAAI/bge-small-en-v1.5) | The model behind this session's vectors: English only, its benchmark results, and the optional instruction prefix for retrieval queries |
| [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard) | Comparing embedding models on retrieval benchmarks. Use it to shortlist, then evaluate on your own questions |
| [OpenAI: Vector embeddings](https://platform.openai.com/docs/guides/embeddings) | A hosted embedding API: models, dimensions and pricing, if you outgrow a local model |
| [Claude docs: Embeddings](https://docs.claude.com/en/docs/build-with-claude/embeddings) | How to choose an embedding provider; Anthropic doesn't offer its own embedding model |

## Vector search and storage

| Resource | Read it for |
|---|---|
| [`numpy.argsort`](https://numpy.org/doc/stable/reference/generated/numpy.argsort.html) | Ranking scores, and the `kind="stable"` option for predictable ties |
| [`numpy.save`](https://numpy.org/doc/stable/reference/generated/numpy.save.html) | The `.npy` format used for the index, and why `allow_pickle` matters when loading |
| [Chroma documentation](https://docs.trychroma.com/) | The embedded vector database from the vector-store notebook: clients, collections, queries and metadata filters |
| [Chroma: Configuring collections](https://docs.trychroma.com/docs/collections/configure) | Choosing the distance function (`cosine`), and the HNSW index settings |
| [Malkov and Yashunin: HNSW](https://arxiv.org/abs/1603.09320) | *Optional.* The approximate nearest-neighbour index most vector databases use, for when brute force is too slow |

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
