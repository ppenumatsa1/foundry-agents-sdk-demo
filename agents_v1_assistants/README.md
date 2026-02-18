# agents_v1_assistants (Foundry Agents)

Azure AI Foundry Agents flow using file search + JSON schema.

## Setup

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Authenticate before running:

- az login

Copy and edit `.env`:

- `AZURE_AI_PROJECT_ENDPOINT`
- `AZURE_AI_MODEL_DEPLOYMENT_NAME`

## Index invoices

python src/index_invoices.py

## Ask a question

python src/run_agent.py "What is the total due on invoice INV-1002?"

## Expected output (example)

You should see a JSON response with `answer` and `top_documents`.

## Example questions

- "What is the total due on invoice INV-1001?"
- "What is the due date for invoice INV-1003?"
- "Who is the vendor on invoice INV-1004?"
- "List all line items on invoice INV-1005."
- "What is the PO number for invoice INV-1002?"

## Expected answers (current data)

- INV-1001 total due: $107.42
- INV-1003 due date: 2025-11-09
- INV-1004 vendor: Northwind IT Services
- INV-1005 line items:
  - Cardboard boxes (large) — Qty 100, Unit Price $1.20, Line Total $120.00
  - Packing tape (bulk) — Qty 10, Unit Price $3.50, Line Total $35.00
- INV-1002 PO number: PO-7810

## Notes

- Uses shared data from ../../data/invoices
- Caches vector store + agent in `.foundry/`
