# swap-desk

The project for the **final readiness assessment**, taken in Session 16. It's an unfinished service for on-call week swaps at Orbital Logistics, a fictional company; all names and data are synthetic.

**Start with [`TASKS.md`](TASKS.md)**: the six tasks, the rules (no AI assistants), the setup commands, and how the assessment is scored. Answer the written questions in [`EXPLANATION.md`](EXPLANATION.md).

```text
swap-desk/
├── TASKS.md            the assessment: read this first
├── EXPLANATION.md      Task 6: your written answers
├── data/rota.json      a sample on-call rota (synthetic)
├── src/swap_desk/
│   ├── rota.py         Task 2
│   ├── models.py       Task 3
│   ├── api.py          Task 3
│   ├── handover.py     Task 4
│   ├── deadlines.py    Task 5 (has bugs)
│   └── cli.py          the swap-desk command (provided)
└── tests/              provided tests; don't edit them. Add your own for Task 5
```
