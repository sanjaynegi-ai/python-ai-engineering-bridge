# Prerequisites

## What you need to know already

This course assumes professional programming experience, typically several years, in at least one language such as Java, C#, JavaScript or TypeScript. You should be comfortable with:

| Area | For example |
|---|---|
| Programming fundamentals | Variables, conditions, loops, functions, classes and objects, collections, exceptions |
| Data formats | Reading and writing JSON; what a schema is |
| HTTP and APIs | Requests and responses, methods, status codes, headers; calling a REST API |
| Git | Clone, commit, branch, pull; reading a diff |
| The command line | Navigating folders, running commands, setting environment variables, in a terminal on macOS or Linux, or PowerShell on Windows |
| Debugging | Reading an error message and a stack trace; using a debugger in some language |
| Application design | Layers, modules, separation of concerns; why tests matter |

You do **not** need any Python, machine-learning or AI experience. The course starts with how Python runs, and builds from there.

To check, take the [entry diagnostic](assessments/entry-diagnostic.md): 22 short questions, about 30 minutes, no Python needed, with answers and a scoring guide. If one of the areas above is new to you, spend an hour on it before the course starts. The live sessions move at the pace of experienced developers.

## What you need on your computer

| Requirement | Notes |
|---|---|
| Windows 10 or 11, macOS, or Linux | Every command in the course is given for Bash and for PowerShell where they differ |
| Permission to install software | `uv`, Git and VS Code install per user. If your work laptop restricts this, sort it out with IT before the course |
| About 5 GB of free disk space | Python, the course environment, and later a local embedding model (about 70 MB) |
| Internet access | To install packages. If you're behind a corporate proxy, see [`docs/troubleshooting.md`](docs/troubleshooting.md) |

Installation, step by step: [`docs/getting-started.md`](docs/getting-started.md). Do it **before** Session 01: setup problems are much easier to solve beforehand than during a live session.

## LLM provider access (from Session 09)

From Session 09, you can call a large language model through a provider's API. That needs an API key, which usually means a paid account with a spending limit. The course default is OpenAI; Session 01, Part 8 shows alternatives, including a free local model with Ollama.

A key is **optional**: every test in the course runs without one, against fakes, and notebooks only make paid calls when you opt in. If your company must approve a provider, start that process early. Read [`docs/api-key-security.md`](docs/api-key-security.md) before you create a key.

## Time

Two 2-hour live sessions each weekend, for 8 weekends, plus **3 to 5 hours** of independent work between weekends.
