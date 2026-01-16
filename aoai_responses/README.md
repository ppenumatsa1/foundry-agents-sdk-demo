# aoai_responses (Responses API)

Responses API flow using Azure OpenAI + file search + JSON schema.

## Setup

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Authenticate before running:

- az login

Copy and edit `.env`:

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_VERSION`
- `MODEL_DEPLOYMENT_NAME`

## Index invoices

python src/index_invoices.py

## Ask a question

python src/ask_responses.py "What is the total due on invoice INV-1002?"

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
- Caches vector store in `.aoai/`
