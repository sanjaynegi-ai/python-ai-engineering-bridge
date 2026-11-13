# Using Claude Code and Other AI Coding Assistants

AI coding assistants are part of professional engineering now, and Session 13 teaches them in depth with [Claude Code](https://code.claude.com/docs/en/overview), Anthropic's coding assistant for the terminal and IDEs. This page explains the course's rules for using assistants, and how to set one up.

## The course's rules

Every workbook is labelled:

| Label | Meaning |
|---|---|
| **Independent** | Do it **without** an AI coding assistant. Read documentation and your notes; ask people. This is where you build the understanding you need to judge AI-generated code later |
| **AI-assisted** | Use an assistant for implementation, following the workbook's process, then test, review and explain the result |
| **AI-review** | Review, debug or improve code an assistant wrote |

Sessions 01 to 12 are **Independent**. That isn't because assistants are bad: if you can't write and debug the code yourself, you can't tell when an assistant's code is wrong, and in a new language it often is, in subtle ways.

Whatever the label: **you're responsible for every line you submit.** You must be able to explain it, test it, and say why it's right.

## The workflow (from Session 13)

**Understand → Plan → Implement → Test → Review → Explain**

1. **Understand** the codebase and the requirement before asking for code. Assistants are good at explaining unfamiliar code; use that.
2. **Plan**: agree the approach, files and tests before any code is written.
3. **Implement** in small steps you can check.
4. **Test**: run the tests yourself. Don't accept "the tests pass" without seeing them pass.
5. **Review** every change as you would a colleague's pull request.
6. **Explain** the important decisions in your own words, in your notes.

## What to check in generated code

| Risk | What to look for |
|---|---|
| Invented APIs | Functions, parameters or packages that don't exist, or don't exist in *your* versions. Check the documentation, and run the code |
| Outdated usage | Patterns from older library versions (Pydantic v1, old SDK call shapes) |
| Missing tests, or weak tests | Tests that can't fail, or that only test the happy path |
| Wrong error handling | Broad `except Exception`, swallowed errors, retries of errors that will never succeed |
| Security problems | Secrets in code, unvalidated input, user text in prompts, unsafe commands |
| Unnecessary complexity | Abstractions, classes or dependencies the problem doesn't need |
| Hidden assumptions | Hard-coded paths, platforms, time zones or encodings |

## Security

- **Don't paste secrets** (keys, `.env` contents, credentials) into an assistant, and don't let it read files containing them.
- **Review commands before you approve them.** An assistant that can run commands can delete files or push code.
- **Untrusted content can carry instructions.** Text in a repository, an issue, a web page or a document can contain instructions aimed at the assistant (*prompt injection*). Be careful with code you didn't write, and keep the assistant's permissions narrow.
- **Respect your employer's rules** about which code and data may be sent to an external service.

## Setting up Claude Code

Follow the official [setup guide](https://code.claude.com/docs/en/setup). It covers installation on macOS, Linux and Windows (with a native installer, Homebrew, WinGet or npm), signing in, and the IDE integrations, including VS Code. Read the [security](https://code.claude.com/docs/en/security) page too.

**Account:** Claude Code needs a Pro, Max, Team, Enterprise or Console account; the free claude.ai plan doesn't include it. Its usage counts against your plan or API billing (`/usage` shows it). If your employer provides or requires a different assistant, use that one: the course's workflow applies to any of them.

**Permission mode for this course:** recent versions start sessions in `auto` mode, where a classifier approves most actions for you. While you're learning, start in **plan mode** to explore (`claude --permission-mode plan`) and use **Manual** mode to implement (`claude --permission-mode manual`), so you see and approve every edit and command. Session 13 explains the modes.

You need it for Session 13. Before then, it's useful for explaining code you don't understand, which is allowed in Independent work: ask it to **explain**, not to write the assignment.
