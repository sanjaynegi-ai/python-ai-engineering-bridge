# Session 14: References

Official documentation first. Each link says *why* it's worth your time. The course pins Python 3.13, chromadb 1.5, pypdf 6.21 and langchain-text-splitters 1.1; when a page describes a different version, trust what your installed version does, and check it with a test.

## Python standard library

| Resource | Read it for |
|---|---|
| [`hashlib`](https://docs.python.org/3.13/library/hashlib.html) | `sha256` and `file_digest`, which hashes a file in blocks without loading it into memory |
| [`pathlib`](https://docs.python.org/3.13/library/pathlib.html) | `rglob`, `relative_to` and `as_posix`: finding files in subfolders and naming them the same way on every operating system |
| [Logging HOWTO](https://docs.python.org/3.13/howto/logging.html) | Loggers per module, levels, and why log calls take `%s` arguments rather than f-strings |
| [`typing.Protocol`](https://docs.python.org/3.13/library/typing.html) | Structural typing: how `Embedder` describes a shape that any class can match |

## Chroma

| Resource | Read it for |
|---|---|
| [Chroma clients](https://docs.trychroma.com/docs/run-chroma/clients) | `PersistentClient` versus `EphemeralClient`, and where the data lives |
| [Manage collections](https://docs.trychroma.com/docs/collections/manage-collections) | Creating, getting, modifying and deleting collections, including their metadata |
| [Configure collections](https://docs.trychroma.com/docs/collections/configure) | The distance function (`cosine` for the capstone) and index settings |
| [Add data](https://docs.trychroma.com/docs/collections/add-data) | Its "Behaviors" section confirms notebook Part 2: an `add` with an existing ID is ignored without an error |
| [Update data](https://docs.trychroma.com/docs/collections/update-data) | `update` and `upsert`, and what happens to IDs that don't exist yet |
| [Delete data](https://docs.trychroma.com/docs/collections/delete-data) | Deleting by ID or by a `where` filter |
| [Metadata filtering](https://docs.trychroma.com/docs/querying-collections/metadata-filtering) | `where` filters, including `$and` and comparisons such as `$gte` |

## Documents and chunking

| Resource | Read it for |
|---|---|
| [pypdf: errors](https://pypdf.readthedocs.io/en/stable/modules/errors.html) | The exception hierarchy: `PdfReadError`, `PdfStreamError`, `EmptyFileError`, and which one to translate |
| [LangChain text splitters](https://docs.langchain.com/oss/python/integrations/splitters/index) | An overview of the splitters, if you choose the library route in Milestone 3 |
| [Splitting recursively](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter) | `RecursiveCharacterTextSplitter`: separators, chunk size and overlap |
| [Split Markdown by headers](https://docs.langchain.com/oss/python/integrations/splitters/markdown_header_metadata_splitter) | `MarkdownHeaderTextSplitter`: headings as metadata, and `strip_headers` |

## Testing

| Resource | Read it for |
|---|---|
| [pytest: how to manage logging](https://docs.pytest.org/en/stable/how-to/logging.html) | The `caplog` fixture: setting the level, reading `caplog.text` and `caplog.records` for canary tests |

## In the course

- Session 11's [concepts notebook](../../session-11/notebooks/01-concepts.ipynb) and [vector store notebook](../../session-11/notebooks/03-building-a-vector-store.ipynb): the building blocks this capstone reuses.
- Session 13's [workbook](../../session-13/workbook/assignment.md): the AI-assisted workflow for Milestones 2 to 6.
- [`docs/using-claude-code.md`](../../../docs/using-claude-code.md): the course's rules for assistants.
