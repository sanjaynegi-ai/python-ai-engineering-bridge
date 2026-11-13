# Capstone Rubric: Internal Knowledge Assistant

The capstone (Project 04, Sessions 14 to 16) is assessed on **evidence in your repository and in your presentation**, not on how much you built. Each criterion has three levels. **"Meets" on every criterion completes Milestone 4.**

Your repository should be tagged `session-16`, with `ARCHITECTURE.md`, `EVALUATION.md` and `PRESENTATION.md` up to date.

| Criterion | Not yet | Meets | Strong |
|---|---|---|---|
| **1. It works** | Some acceptance tests fail, or the API or UI doesn't start | All acceptance and integration tests pass; `ingest`, `ask`, the API and the UI work on the sample documents, offline | The same with the real embedding model, and a live run with an LLM recorded in `EVALUATION.md` |
| **2. Ingestion is safe to repeat** | Re-running ingestion duplicates, misses edits, or stops on a broken file | A second run embeds nothing; edits, deletions and broken files behave as specified, and you can show it | You've measured it (time and embedding calls for a first and a second run) and explained the cost |
| **3. Answers are grounded** | Answers can cite sources that weren't given, or the model is called when nothing was retrieved | Citations are checked; "not found" happens at both levels; only cited sources are returned | You've shown an ungrounded answer being refused, and explained what a valid citation does and doesn't prove |
| **4. Errors and security** | Tracebacks or document text reach users or logs; secrets in code or Git | Each failure maps to the right status or message; no question, answer or document text in logs; no secrets committed | You can point to the test that proves each property |
| **5. Tests** | Only the provided tests | The provided tests, plus your own unit tests for the decisions you made | Your tests caught a real bug of yours, and `ARCHITECTURE.md` says which |
| **6. Evaluation** | No evaluation, or only the totals | `EVALUATION.md` explains every listed miss, and justifies the threshold with questions you didn't tune on | You changed something (chunking, threshold, prompt) and compared all four rates before and after |
| **7. Observability** | Free-text logs only | JSON logs with an `answer`, `ingest` and `request` event, and a request ID linking a request to its answer | You've used the logs to answer an operational question, such as the not-found rate or slow requests |
| **8. Design and documentation** | No architecture notes, or notes that don't match the code | `ARCHITECTURE.md` describes the modules, the path of a question, your decisions and known limitations | Limitations come with what you'd do about them, in priority order |
| **9. Explanation** | You can't explain parts of your own code | In the demonstration and questions, you explain and defend your design, including what an assistant wrote | You discuss alternatives you rejected, and why |
| **10. AI-assisted engineering** | No record of how you used an assistant, or assistant output accepted unread | Your reflections say where you used one, what you checked, and what you changed | You show a concrete case where review caught an assistant's mistake |

## The demonstration (Session 16)

Five minutes, then questions:

1. The problem, in one sentence, and the architecture diagram of **your** code.
2. One answered question, and one "not found", live (offline mode is fine).
3. One design decision you'd defend, with the alternative you rejected.
4. One known limitation, and what you'd do about it next.

Questions will ask you to explain a part of your code you didn't mention. "An assistant wrote that" is an honest answer only if you can continue with what it does and why you kept it.
