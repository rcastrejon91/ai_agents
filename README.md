# AI Agents

This repository contains sample FastAPI-based AI agent services. Each agent
implements a small task that could be monetized as a standalone API. The
available agents are:

- **FinanceAgent** – calculates return on investment via `/roi`.
- **HealthcareAgent** – computes Body Mass Index via `/bmi`.
- **LegalAgent** – provides very basic text summarization via `/summarize`.
- **RetailAgent** – calculates discounted prices via `/discount`.

## Running an agent

Each agent class can be started individually:

```bash
python -m agents.finance_agent
```

The default ports are 8001–8004 for the four agents. Once running, send JSON
payloads to the respective endpoints to receive results.

These simple examples demonstrate how domain-specific services can be created
and offered through an API for potential monetization.
