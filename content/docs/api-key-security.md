# API Key Security

An API key is a password that also spends money. A leaked key can run up a bill, exhaust your rate limits, or expose your account's data. This page covers keeping keys safe in this course, and what to do if one leaks.

## Where keys live

**In a `.env` file, never in code or notebooks.**

```text
# .env (in the folder where you run your code)
OPENAI_API_KEY=your-key-here
```

- `.env` is listed in `.gitignore` in the course repository and every project starter, so Git won't commit it. Check, in any repository: `git check-ignore -v .env` should print the `.gitignore` line that ignores it.
- `.env.example` is the committed template: variable names, placeholder values and comments, never real keys.
- Course code reads keys with `pydantic-settings` as a `SecretStr`, which shows `**********` when printed or logged (Session 06). Real values are taken out only where they're needed, with `.get_secret_value()`.
- Notebooks report **whether** a key is set, never its value. Don't print keys, even partly, "to check": partial keys end up in screenshots and logs.

## Before you create a key

1. **Set a spending limit** in the provider's dashboard: a monthly budget, and an alert well below it.
2. **Create a key just for this course**, with a name that says so. Then you can revoke it without affecting anything else.
3. Use the **narrowest permissions** the provider offers. Course work only needs model access.

## Sharing your screen, and asking for help

- Close `.env` before sharing your screen, and don't open it in an editor during a live session.
- When you post an error, check it for keys first. Some providers' error messages repeat part of the key; the course's code avoids that, but other code might not.
- Never send a key in chat, email or an issue, not even to an instructor.

## If a key leaks

If a key was committed, pushed, pasted, shown on screen or posted anywhere:

1. **Revoke it immediately** in the provider's dashboard, and create a new one. Do this first. Bots scan public repositories for keys within minutes.
2. Check the provider's **usage page** for activity you don't recognise.
3. Put the new key in `.env`.
4. **Removing the key from the code isn't enough.** It's still in the Git history. Once the key is revoked, the history doesn't matter much, which is why revoking comes first. Rewriting published history is disruptive, and rarely worth it once the key is dead.

## In your own projects

- Commit a `.env.example`; never commit `.env`.
- Read secrets from the environment, through a settings object. Fail with a clear message, naming the variable, when one is missing.
- Keep secrets out of logs, exception messages, `repr()` and test fixtures. Tests should use obviously fake values such as `not-a-real-key`.
- Don't send secrets, credentials or personal data to an LLM in a prompt (Session 09).
