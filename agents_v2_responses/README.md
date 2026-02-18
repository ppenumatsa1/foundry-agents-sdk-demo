# agetns_v2_responses_latest (Foundry + Responses API)

Azure AI Foundry agent creation via `azure-ai-projects` and invocation via the Responses API.

## Setup

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Authenticate before running:

- az login

Copy and edit `.env`:

- `AZURE_AI_PROJECT_ENDPOINT`
- `AZURE_AI_MODEL_DEPLOYMENT_NAME`
- `AZURE_AI_AGENT_NAME` (optional)

## Index invoices

python3 src/index_invoices.py

## Ask a question

python3 src/run_agent.py "What is the total due on invoice INV-1002?"

## Expected output (example)

You should see a JSON response with `answer` and `top_documents`.

## Example questions

- "What is the total due on invoice INV-1001?"
- "What is the due date for invoice INV-1003?"
- "Who is the vendor on invoice INV-1004?"
- "List all line items on invoice INV-1005."
- "What is the PO number for invoice INV-1002?"

## Notes

- Uses shared data from ../../data/invoices
- Caches vector store + agent in `.foundry/`
