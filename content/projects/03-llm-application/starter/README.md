# incident-triage

LLM-assisted triage for the Orbital Logistics on-call team. It reads free-text incident reports and returns a structured triage for each: priority, owning team, category, affected system, a one-line summary and tags. Orbital Logistics is a fictional company, and all data in this project is synthetic.

This is **Project 03**. It grows over three sessions:

| Session | What's added |
|---|---|
| 09 | Direct integration with OpenAI's Responses API: structured output, validation, errors, token usage and cost (**this stage**) |
| 10 | The same triage with LangChain, compared with the direct version |
| 12 | A LangGraph workflow that validates and routes triage results |

## Setup

```bash
uv sync
```

To call the LLM, copy `.env.example` to `.env` and set `OPENAI_API_KEY`. Without a key, use `--offline`, which applies simple keyword rules instead: no network and no cost.

## Usage

```bash
uv run incident-triage data/reports.jsonl --offline     # keyword rules, free
uv run incident-triage data/reports.jsonl               # the LLM: costs a little per report
uv run incident-triage data/reports.jsonl --out out/today.json
```

| Exit code | Meaning |
|---:|---|
| `0` | Every report was triaged |
| `1` | Some reports couldn't be triaged (refusal, invalid output, provider unavailable); listed on stderr |
| `2` | No run: invalid settings, a bad reports file, or the provider rejected the key or model |

Each request's token usage is recorded. Set `LLM_INPUT_USD_PER_MILLION` and `LLM_OUTPUT_USD_PER_MILLION` to see the cost.

## Project layout

```text
incident-triage/
├── .env.example            documented settings; copy to .env
├── data/reports.jsonl      sample incident reports (synthetic)
├── src/incident_triage/
│   ├── models.py           IncidentReport, TriageResult (the LLM's output contract), Usage, runs
│   ├── settings.py         Settings (pydantic-settings)
│   ├── prompts.py          the instructions sent with every request
│   ├── llm.py              the Triager protocol and OpenAITriager
│   ├── offline.py          KeywordTriager: a rule-based baseline
│   ├── service.py          triage_all: a batch, with per-report failures
│   ├── loading.py          reading JSON Lines report files
│   ├── errors.py           TriageError and its subclasses
│   └── cli.py              the incident-triage command
└── tests/
    ├── conftest.py         fake_openai: the Responses API, faked at the HTTP level
    ├── acceptance/         provided tests; do not edit
    └── unit/               your own tests
```

## Development

```bash
uv run pytest           # no test makes a real API call
uv run ruff check .
uv run ruff format .
```
