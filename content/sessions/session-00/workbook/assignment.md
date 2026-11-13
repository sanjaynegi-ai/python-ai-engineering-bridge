# Assignment: GenAI Application Design Brief

## Business scenario

Choose a recurring information or decision-support problem from a domain you understand: incident response, quality assurance, customer support, compliance, developer enablement or another professional setting.

## Learning objectives

- Select the smallest suitable architecture.
- Identify evidence, risks and evaluation signals before selecting a framework.
- Explain an AI design in ordinary engineering language.

## Deliverable

Create `genai-design-brief.md`, limited to roughly two pages.

## Requirements

Your brief must contain:

1. **Problem and users:** who needs what decision or output?
2. **Architecture choice:** direct LLM call, RAG, deterministic workflow, agent or agentic RAG.
3. **Why this choice:** include one simpler alternative you rejected.
4. **Inputs and data:** what enters the system, and what must not be sent to a provider?
5. **Model route:** hosted provider, OpenRouter gateway, local Ollama, or local Hugging Face model.
6. **Failure modes:** at least two, including one non-model failure.
7. **Evaluation:** one quality measure and one operational measure.
8. **Human control:** where review, approval or escalation occurs.
9. **Architecture sketch:** boxes and arrows are sufficient.

## Optional experiment

Run one provider example from the concepts notebook. Record the model, elapsed time, result, and one observation. Never submit an API key or `.env` file.

## Acceptance criteria

- The architecture matches the problem rather than using an agent by default.
- Retrieval is included only when external or changing knowledge is required.
- The brief identifies testable behavior and a safe failure path.
- A colleague could challenge the design without needing to decode framework terminology.

## Reflection

What evidence would make you replace your chosen architecture with a simpler or more capable one?
