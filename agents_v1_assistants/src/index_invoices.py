import json
import os
from pathlib import Path

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FilePurpose
from azure.identity import AzureCliCredential
from dotenv import load_dotenv


def load_env() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)


def load_cached_vector_store_id() -> str | None:
    cache_path = Path(__file__).resolve().parents[1] / ".foundry" / "vector_store.json"
    if not cache_path.exists():
        return None
    data = json.loads(cache_path.read_text())
    return data.get("vector_store_id")


def save_vector_store_id(vector_store_id: str) -> None:
    output_dir = Path(__file__).resolve().parents[1] / ".foundry"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "vector_store.json"
    output_path.write_text(json.dumps({"vector_store_id": vector_store_id}, indent=2))


def main() -> None:
    load_env()

    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT") or os.environ.get(
        "FOUNDRY_PROJECT_ENDPOINT"
    )
    if not endpoint:
        raise ValueError("AZURE_AI_PROJECT_ENDPOINT is required")

    credential = AzureCliCredential(additionally_allowed_tenants=["*"])
    agents_client = AgentsClient(endpoint=endpoint, credential=credential)

    cached_id = load_cached_vector_store_id()
    if cached_id:
        try:
            agents_client.vector_stores.get(cached_id)
            print(f"Reusing cached vector store id: {cached_id}")
            return
        except Exception:
            print("Cached vector store not found; creating a new one")

    print("Starting index: scanning invoices and uploading...")

    invoice_dir = Path(__file__).resolve().parents[2] / "data" / "invoices"
    files = sorted(invoice_dir.glob("*.txt"))
    if not files:
        raise ValueError(f"No invoice files found in {invoice_dir}")

    print(f"Found {len(files)} files")
    file_ids = []
    for file_path in files:
        print(f"Uploading {file_path.name}...")
        uploaded = agents_client.files.upload_and_poll(
            file_path=str(file_path),
            purpose=FilePurpose.AGENTS,
        )
        file_ids.append(uploaded.id)

    print("Creating vector store...")
    vector_store = agents_client.vector_stores.create_and_poll(
        name="InvoiceVectorStore",
        file_ids=file_ids,
    )

    print(f"Vector store created and indexed: {vector_store.id}")
    save_vector_store_id(vector_store.id)
    print(
        "Saved vector store ID to: "
        f"{Path(__file__).resolve().parents[1] / '.foundry' / 'vector_store.json'}"
    )


if __name__ == "__main__":
    main()
