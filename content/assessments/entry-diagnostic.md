# Entry Diagnostic

**Time:** about 30 minutes · **Before:** Session 01 · **Python needed:** none

This course assumes you're an experienced developer in some other language. This self-check tells you whether that's true for the areas the course builds on, listed in [`PREREQUISITES.md`](../PREREQUISITES.md), and where to spend an hour before the course if it isn't. It isn't graded, and nobody sees your answers.

**How to use it:** answer each question on paper or in a text file **before** opening "Show answer". Then score yourself: 1 point for a correct answer, half a point for a partly correct one. Code is written in a neutral, JavaScript-like style; read it as you would in your own language.

---

## A. Programming reasoning

### A1. Predict the output

```text
total = 0
for n in [3, 8, 2, 7, 4]:
    if n > 3:
        total = total + n
    else:
        total = total - 1
print(total)
```

<details>
<summary>Show answer</summary>

**17.** 3 is not greater than 3, so total becomes -1; then +8 = 7; 2 gives 6; +7 = 13; +4 = 17. The trap is the boundary: `>` versus `>=`.

</details>

### A2. Who sees the change?

```text
function addDefault(tags) {
    tags.push("unassigned")
    return tags
}

original = ["vpn", "berlin"]
result = addDefault(original)
print(original.length)
```

What's printed, and why?

<details>
<summary>Show answer</summary>

**3.** The function receives a reference to the same list object, not a copy, so `push` changes the caller's list too. `original` and `result` are the same list. This is how lists and objects behave in Java, C#, JavaScript and Python alike, and it causes real bugs: a function that "returns a modified copy" but actually mutates its input.

</details>

### A3. Choosing a collection

You need to check, a million times, whether an incident ID is in a set of 200,000 known IDs. Would you keep the known IDs in a list (array) or in a hash set? Why?

<details>
<summary>Show answer</summary>

**A hash set.** Checking membership in a list means scanning it, on average about 100,000 comparisons per check. A hash set answers in roughly constant time. With a million checks, that's the difference between seconds and hours. Recognising "membership test inside a loop" as a performance smell is the skill being checked.

</details>

### A4. Exceptions and `finally`

```text
function load() {
    try {
        print("open")
        throw new Error("disk full")
        print("write")
    } finally {
        print("close")
    }
}

try { load() } catch (e) { print("caught: " + e.message) }
```

What's printed, in order?

<details>
<summary>Show answer</summary>

```text
open
close
caught: disk full
```

`write` never runs, because the exception stops the `try` block. `finally` runs before the exception leaves `load`, and only then does the caller's `catch` see it. Cleanup in `finally` (or `using`, or try-with-resources) is what keeps files and connections from leaking.

</details>

---

## B. JSON

### B1. Which of these are valid JSON?

```text
1.  {"id": 42, "tags": ["vpn", "berlin"]}
2.  {'id': 42}
3.  {"id": 42, "tags": ["vpn",],}
4.  {"id": "42", "resolved": null}
5.  {"id": 42 // the ticket number
    }
```

<details>
<summary>Show answer</summary>

**1 and 4.** 2 uses single quotes, which JSON doesn't allow. 3 has trailing commas. 5 has a comment, which JSON doesn't support either. 4 is valid; whether `"42"` should be a string or a number is a design question, not a syntax error.

</details>

### B2. Navigating a document

```json
{
  "team": "network",
  "incidents": [
    {"id": "INC-1", "priority": "P2", "assignee": {"name": "Amara", "email": "amara@example.com"}},
    {"id": "INC-2", "priority": "P1", "assignee": null}
  ]
}
```

1. How do you reach Amara's email, in your language's syntax?
2. What will code that reads `incidents[1].assignee.name` do, and how should it be written instead?

<details>
<summary>Show answer</summary>

1. Something like `data["incidents"][0]["assignee"]["email"]` or `data.incidents[0].assignee.email`.
2. It fails (a null reference error, `TypeError`, or `NullPointerException`), because the second incident's `assignee` is `null`. Check for `null` first, or use your language's safe navigation (`?.`). Real data is full of optional fields; code that assumes every field is present is the most common JSON bug.

</details>

### B3. Dates in JSON

JSON has no date type. How would you put "the incident was opened at 09:30 on 2 November 2026" in a JSON document so that any system reads it correctly?

<details>
<summary>Show answer</summary>

As an **ISO 8601 string with a time zone**, for example `"2026-11-02T09:30:00+01:00"` or, in UTC, `"2026-11-02T08:30:00Z"`. Without the offset, a reader in another time zone gets a different moment. Unix timestamps (`1793608200`) also work, but they're unreadable for people. Half a point for ISO 8601 without mentioning the time zone.

</details>

---

## C. HTTP and APIs

### C1. Status codes

Which status code fits each response?

1. A new ticket was created.
2. The request body is valid JSON, but `priority` is `"P9"`.
3. The caller sent no API key.
4. The ticket ID doesn't exist.
5. The service is overloaded and asks the caller to retry later.

<details>
<summary>Show answer</summary>

1. **201** Created (200 is acceptable but less precise).
2. **422** Unprocessable Content (or **400** Bad Request, which many APIs use for all validation errors).
3. **401** Unauthorized (meaning "not authenticated"). 403 is for "authenticated, but not allowed".
4. **404** Not Found.
5. **503** Service Unavailable, or **429** Too Many Requests if it's about this caller's rate. Either usually comes with a `Retry-After` header.

Score 1 point for at least four correct.

</details>

### C2. Safe to retry?

A request times out, and your client doesn't know whether the server processed it. Is it safe to send it again if it was a `GET`? A `PUT` that sets a ticket's status? A `POST` that creates a ticket?

<details>
<summary>Show answer</summary>

`GET` and `PUT` are **idempotent**: doing them twice has the same effect as once, so retrying is safe. A `POST` that creates something is **not**: retrying can create two tickets. APIs handle this with idempotency keys (a client-chosen ID the server uses to recognise a repeat), or by checking before creating. This matters a lot later, when you call LLM APIs and other services that time out.

</details>

### C3. Timeouts

Why should every HTTP call in a service have a timeout? What happens without one?

<details>
<summary>Show answer</summary>

Without a timeout, a call to a server that stops responding can wait for minutes, or forever. Each stuck call holds a thread, connection or request slot, so a slow dependency gradually makes **your** service unresponsive too. A timeout turns "hangs" into an error you can handle: retry, fall back, or report it. Many HTTP libraries' defaults are very long or infinite, so you set it yourself.

</details>

### C4. Where does the key go?

An API needs a secret key. Should the client send it in the URL (`?api_key=...`) or in a header (`Authorization: Bearer ...`)? Why?

<details>
<summary>Show answer</summary>

**In a header.** URLs end up in server access logs, proxy logs, browser history and monitoring tools, so a key in a URL leaks to everyone who can read those. Headers aren't logged by default. Wherever it's sent, the key itself belongs in an environment variable or a secret manager, never in code or in Git.

</details>

---

## D. Git

### D1. Everyday commands

Which commands would you use to:

1. create a new branch called `fix-timeout` and switch to it;
2. see what you've changed but not yet committed;
3. throw away your uncommitted changes to one file, `config.json`?

<details>
<summary>Show answer</summary>

1. `git switch -c fix-timeout` (or `git checkout -b fix-timeout`).
2. `git diff` (and `git status` for the list of files).
3. `git restore config.json` (or `git checkout -- config.json`). It can't be undone, so check with `git diff config.json` first.

Score 1 point for all three, half for two.

</details>

### D2. Reading a diff

```diff
@@ -12,7 +12,7 @@ def page_on_call(incident):
     if incident.priority == "P1":
-        notify(incident.team, delay_minutes=10)
+        notify(incident.team, delay_minutes=0)
     return incident
```

What changed, in one sentence? What would you ask the author in a code review?

<details>
<summary>Show answer</summary>

P1 incidents now notify the team immediately instead of after 10 minutes: the `-` line was removed and the `+` line added; the others are context. A good review question: *why was there a delay, and is there a test showing P1 notifications are now immediate (and that other priorities didn't change)?*

</details>

### D3. A leaked secret

You committed a file containing an API key and pushed it. A colleague suggests deleting the key from the file and committing again. Is that enough?

<details>
<summary>Show answer</summary>

**No.** The key is still in the repository's **history**: anyone with a clone can find it in the earlier commit. The only reliable fix is to **revoke the key** at the provider and create a new one. Rewriting history can remove it from the repository, but copies may already exist. Then make sure secrets live in an ignored `.env` file or a secret manager.

</details>

---

## E. The command line

### E1. Environment variables

How do you set an environment variable `LOG_LEVEL` to `debug` for the current terminal session, in Bash (macOS or Linux), and in PowerShell (Windows)?

<details>
<summary>Show answer</summary>

- Bash: `export LOG_LEVEL=debug`
- PowerShell: `$env:LOG_LEVEL = "debug"`

Either one is enough for the point if you use only one shell. Both last only for that terminal session. The course gives commands for both shells wherever they differ.

</details>

### E2. Paths

You're in `/home/sam/projects/api`. Where do these refer to?

1. `..`
2. `./tests`
3. `../web/README.md`
4. `/tmp`

<details>
<summary>Show answer</summary>

1. `/home/sam/projects`
2. `/home/sam/projects/api/tests`
3. `/home/sam/projects/web/README.md`
4. `/tmp`: an absolute path, independent of the current folder.

Windows works the same way with backslashes (and PowerShell accepts forward slashes too).

</details>

### E3. "Command not found"

You install a tool, open a terminal, type its name, and get "command not found" (or "is not recognized as the name of a cmdlet"). What are the two most likely causes?

<details>
<summary>Show answer</summary>

1. The folder the tool was installed into **isn't on your `PATH`**, the list of folders the shell searches for commands.
2. The terminal was **opened before the installation** changed `PATH`, so it still has the old value: open a new one.

Half a point for one of them. The course's setup guide uses exactly this knowledge when `uv` isn't found after installing it.

</details>

---

## F. Debugging

### F1. Reading a stack trace

```text
Error: Cannot read properties of undefined (reading 'email')
    at formatAssignee (src/report/format.js:41:22)
    at buildRow (src/report/rows.js:18:10)
    at Array.map (<anonymous>)
    at buildReport (src/report/index.js:7:30)
    at main (src/cli.js:12:3)
```

(A Java or C# stack trace has the same shape.) Where did the error happen, and where would you look first to understand **why**?

<details>
<summary>Show answer</summary>

It happened in `formatAssignee`, at `format.js` line 41, reading `.email` from something that was `undefined`: probably an incident without an assignee. Look first at line 41, then one frame up, at `rows.js` line 18, to see what was passed in. The frames read from the most recent call (top) down to the entry point (bottom). Python's tracebacks are printed the other way round, most recent call **last**, which the course points out in Session 03.

</details>

### F2. The flaky test

A test passes on your machine and fails about one time in five in CI. Name three likely causes.

<details>
<summary>Show answer</summary>

Any three of: dependence on **the current time or time zone**; dependence on **test order** or on shared state left by another test; **randomness** without a fixed seed; **timing** (sleeps, timeouts, races between threads); **unordered collections** compared as if ordered; **external services** or the network; different **environment** settings in CI (locale, file paths, line endings). Score 1 point for three plausible causes.

</details>

### F3. A vague bug report

A user reports: *"The nightly export is sometimes empty."* What are your first three steps?

<details>
<summary>Show answer</summary>

Something like:

1. **Get evidence:** which nights, the logs and the exit status of those runs, the input data on those nights.
2. **Find the pattern:** what's different about the empty nights (no input files, a failed upstream job, a time-zone boundary, a deploy)?
3. **Reproduce it** with that input, ideally as a failing test, **before** changing any code.

The course calls this **Observe → Hypothesize → Inspect → Fix → Verify**. Half a point if your first step was to change code.

</details>

---

## G. Application design

### G1. Where does it belong?

An HTTP endpoint creates an incident. Where would you put each of these: the HTTP routing and status codes; the check that `priority` is one of P1 to P4; the rule "P1 incidents page the on-call engineer"; the SQL that saves the incident?

<details>
<summary>Show answer</summary>

- **HTTP routing and status codes:** the API (controller) layer.
- **Is `priority` valid:** input validation at the boundary, usually a request model or schema in the API layer.
- **P1 pages on-call:** the service (domain) layer, independent of HTTP, so a CLI or a queue consumer gets the same rule.
- **The SQL:** a data-access (repository) layer.

Exact names don't matter; separating "how it's called", "what the rules are" and "where it's stored" does. Score 1 point if the business rule isn't in the controller or the SQL.

</details>

### G2. Testing something that calls an external API

Your service calls a paid external API. Why would your automated tests replace that API with a fake (a mock or stub), and what does that leave untested?

<details>
<summary>Show answer</summary>

**Why fake it:** tests become fast, free, deterministic, and runnable without network or credentials, and you can simulate failures (timeouts, 500s, bad data) that the real API rarely produces on demand.

**What it leaves untested:** whether the real API behaves the way your fake assumes. So you keep the fake honest (match the real response format, check it occasionally against the real service), and run a small number of real calls deliberately. The course does exactly this with LLM APIs from Session 09.

</details>

---

## Scoring

Add up your points for each area.

| Area | Questions | Your score |
|---|---|---:|
| A. Programming reasoning | A1–A4 | /4 |
| B. JSON | B1–B3 | /3 |
| C. HTTP and APIs | C1–C4 | /4 |
| D. Git | D1–D3 | /3 |
| E. The command line | E1–E3 | /3 |
| F. Debugging | F1–F3 | /3 |
| G. Application design | G1–G2 | /2 |
| **Total** | | **/22** |

## What your score means

- **18 or more, and no area below half:** you're ready. Go to [`docs/getting-started.md`](../docs/getting-started.md) and set up your machine before Session 01.
- **An area below half:** spend an hour on it before Session 01, using the suggestions below, then try that area's questions again. The course moves at the pace of experienced developers, and doesn't stop to teach these.
- **Below 13 in total:** the course will be hard going. Talk to whoever organised your place before it starts; a general programming course first may serve you better.

| Area | An hour well spent |
|---|---|
| A. Programming reasoning | Write a few small programs in your own language that use lists, maps and exceptions; predict their output before running them |
| B. JSON | [Introducing JSON](https://www.json.org/json-en.html) (the whole grammar fits on one page); practise reading a real API response |
| C. HTTP and APIs | MDN's [overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview) and [HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status) |
| D. Git | [Pro Git](https://git-scm.com/book/en/v2), chapters 2 and 3 |
| E. The command line | Your shell's basics: changing folders, paths, environment variables and `PATH`. [`docs/getting-started.md`](../docs/getting-started.md) gives every command the course needs |
| F. Debugging | Run a program in your language's debugger: set a breakpoint, step, inspect variables. Read the stack trace of every error you meet this week |
| G. Application design | Look at a service you know and name its layers: where are requests handled, rules applied, data stored? |
