# Session 16: References

Official documentation first. Each link says *why* it's worth your time.

## Logging and observability

| Resource | Read it for |
|---|---|
| [Logging HOWTO](https://docs.python.org/3.13/howto/logging.html) | Loggers, handlers, formatters and levels: how a record travels from `logger.info` to a line of output |
| [Logging Cookbook](https://docs.python.org/3.13/howto/logging-cookbook.html) | Adding contextual information to records (filters and record factories), and structured logging |
| [`logging` reference](https://docs.python.org/3.13/library/logging.html) | `LogRecord` attributes, `Formatter`, `Filter`, and `setLogRecordFactory` |
| [`contextvars`](https://docs.python.org/3.13/library/contextvars.html) | Context variables: per-request values that follow `asyncio` tasks |
| [FastAPI: middleware](https://fastapi.tiangolo.com/tutorial/middleware/) | `@app.middleware("http")`: code that runs around every request |

## Testing

| Resource | Read it for |
|---|---|
| [pytest: how to manage logging](https://docs.pytest.org/en/stable/how-to/logging.html) | `caplog`: checking what was logged, record by record |
| [FastAPI: testing](https://fastapi.tiangolo.com/tutorial/testing/) | `TestClient`, used by the integration tests |

## The assessment

- [`assessments/python-readiness.md`](../../../assessments/python-readiness.md): what "ready" means, the evidence, the standard, and what to revisit.
- [`assessments/final-assessment.md`](../../../assessments/final-assessment.md): the final assessment's format, rules and scoring.
- [`assessments/capstone-rubric.md`](../../../assessments/capstone-rubric.md): how the capstone and your demonstration are assessed.

## In the course

- Session 04's [concepts notebook](../../session-04/notebooks/01-concepts.ipynb): pytest, fixtures and the debugger.
- Session 13's [workbook](../../session-13/workbook/assignment.md): reviewing code you didn't write, including your assistant's.
- Session 15's [concepts notebook](../../session-15/notebooks/01-concepts.ipynb): the evaluation your logs now complement.

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
