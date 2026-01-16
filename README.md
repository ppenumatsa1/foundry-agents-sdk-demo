# foundry-agent-sdk-demo

Goal: Create an invoice workflow that ingests invoice documents into a vector store, then sets up an agent that uses a file search tool over that vector store. The agent answers questions via RAG and returns structured JSON output.

This monorepo compares the same workflow across multiple SDKs (Azure AI Foundry Agents v1 via `azure-ai-agents`, Azure OpenAI Responses API, and Azure AI Foundry Agents v2 via `azure-ai-projects`), using **shared data** only.

## SDK comparison

| Subproject           | SDK(s)                  | SDK status         | Foundry agents version | Tracing / evals (OOTB)                                                        | Notes                                                                                    |
| -------------------- | ----------------------- | ------------------ | ---------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| agents_v1_assistants | `azure-ai-agents`       | GA                 | v1                     | Tracing: supported (OpenTelemetry + App Insights). Evals: via Foundry portal. | Foundry Agents v1 via `azure-ai-agents` (Assistants API) with file search + JSON schema. |
| aoai_responses       | `openai` (Azure OpenAI) | GA                 | N/A                    | Tracing: not built-in (optional via OpenTelemetry). Evals: N/A.               | Uses Responses API + file search + JSON schema.                                          |
| agents_v2_responses  | `azure-ai-projects`     | Pre-release (beta) | v2                     | Tracing: supported (OpenTelemetry + App Insights). Evals: via Foundry portal. | Foundry Agents v2 via `azure-ai-projects` + Responses API.                               |

## Subprojects

1. **agents_v1_assistants**

   - Azure AI Foundry Agents flow (Assistants API) using file search + JSON schema.
   - Instructions: [agents_v1_assistants/README.md](agents_v1_assistants/README.md)

2. **aoai_responses**

   - Responses API flow using Azure OpenAI + file search + JSON schema.
   - Instructions: [aoai_responses/README.md](aoai_responses/README.md)

3. **agents_v2_responses**
   - Azure AI Foundry Agents (v2) created via `azure-ai-projects` and invoked via the Responses API with JSON schema.
   - Instructions: [agents_v2_responses/README.md](agents_v2_responses/README.md)

## Shared data

All subprojects read invoice files from:

foundry-agent-sdk-demo/data/invoices

## Quick start

Each subproject has its own:

- `requirements.txt`
- `.env` and `.env.example`
- `README.md`
- `tests/`

Go into the subproject folder and follow its README.
