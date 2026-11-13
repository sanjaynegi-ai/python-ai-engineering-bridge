# Session 01: References

Official documentation first. Each link says *why* it's worth your time, so you can pick what you need instead of reading everything.

## uv

| Resource | Read it for |
|---|---|
| [Installing uv](https://docs.astral.sh/uv/getting-started/installation/) | All installation methods, upgrading uv (`uv self update`), shell autocompletion |
| [Working on projects](https://docs.astral.sh/uv/guides/projects/) | The `uv init` → `uv add` → `uv run` workflow you used in the workbook |
| [Project structure and files](https://docs.astral.sh/uv/concepts/projects/layout/) | What `pyproject.toml`, `.python-version`, `.venv` and `uv.lock` are for |
| [Managing dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/) | Dependency groups (`--dev`), version specifiers, and sources |
| [Locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/) | `--locked`, `--frozen`, upgrading locked packages |
| [Installing Python](https://docs.astral.sh/uv/guides/install-python/) | How uv finds, downloads and selects Python versions |

## Python runtime and environments

| Resource | Read it for |
|---|---|
| [Python tutorial: Virtual Environments and Packages](https://docs.python.org/3/tutorial/venv.html) | The standard-library view of virtual environments, which uv builds on |
| [`venv`: How venvs work](https://docs.python.org/3/library/venv.html#how-venvs-work) | What `sys.prefix`, `sys.base_prefix` and `pyvenv.cfg` mean, precisely |
| [The import system: searching](https://docs.python.org/3/reference/import.html#searching) | How `import` finds modules (`sys.path`, `sys.modules`) |
| [`sys.path` initialization](https://docs.python.org/3/library/sys_path_init.html) | Exactly which directories end up on `sys.path`, and in what order |
| [`__main__`: top-level code environment](https://docs.python.org/3/library/__main__.html) | The `if __name__ == "__main__":` idiom, explained in full |
| [`dis`: disassembler for bytecode](https://docs.python.org/3/library/dis.html) | Optional: reading bytecode, if you're curious about the execution model |
| [Python release status](https://devguide.python.org/versions/) | Which Python versions are supported, and until when |

## Packaging standards

| Resource | Read it for |
|---|---|
| [Writing your `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) | The standard `[project]` table, independent of any one tool |
| [Version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/) | The formal rules behind `>=`, `~=`, `==` and friends |

## LLM providers (for Part 8)

| Resource | Read it for |
|---|---|
| [OpenAI: API quickstart](https://developers.openai.com/api/docs/quickstart) | Creating a key and making a first request with the `openai` SDK |
| [OpenAI: deprecations](https://developers.openai.com/api/docs/deprecations) | Which models are being retired, when, and their recommended replacements |
| [Anthropic: models overview](https://platform.claude.com/docs/en/about-claude/models/overview) | Current Claude model IDs and how they differ |
| [OpenRouter: quickstart](https://openrouter.ai/docs/quickstart) | Using the `openai` SDK with OpenRouter's `base_url` |
| [OpenRouter: models](https://openrouter.ai/models) | Browsing models and their `vendor/model` IDs |
| [Ollama: OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility) | Calling local models through the `openai` SDK |
| [Anthropic: pricing](https://platform.claude.com/docs/en/about-claude/pricing) | Current per-token prices for Claude models, such as Haiku versus Opus |

## Embeddings (for Part 9)

| Resource | Read it for |
|---|---|
| [OpenAI: embeddings guide](https://developers.openai.com/api/docs/guides/embeddings) | `text-embedding-3-small`/`-large`, the `dimensions` parameter, use cases |
| [fastembed documentation](https://qdrant.github.io/fastembed/) | Getting started, the `TextEmbedding` API, caching |
| [fastembed: supported models](https://qdrant.github.io/fastembed/examples/Supported_Models/) | Every model fastembed can run, with sizes and vector lengths |
| [fastembed on GitHub](https://github.com/qdrant/fastembed) | Source, releases, and issues if something misbehaves |

## Editors and notebooks

| Resource | Read it for |
|---|---|
| [Python environments in VS Code](https://code.visualstudio.com/docs/python/environments) | Selecting an interpreter, and how VS Code discovers `.venv` |
| [Jupyter notebooks in VS Code](https://code.visualstudio.com/docs/datascience/jupyter-notebooks) | Selecting a kernel, running cells, debugging notebooks |
| [JupyterLab documentation](https://jupyterlab.readthedocs.io/en/stable/) | If you prefer the browser-based notebook interface |

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
