# foundry-agent-sdk-demo

Goal: Create an invoice workflow that ingests invoice documents into a vector store, then sets up an agent that uses a file search tool over that vector store. The agent answers questions via RAG and returns structured JSON output.

This monorepo compares the same workflow across multiple SDKs (Azure AI Foundry Agents v1 via `azure-ai-agents`, Azure OpenAI Responses API, and Azure AI Foundry Agents v2 via `azure-ai-projects`), using **shared data** only.

## Subprojects

1. **agents_v1_assistants**

   - Azure AI Foundry Agents flow using file search + JSON schema.
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
