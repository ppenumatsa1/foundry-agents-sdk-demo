import json
import os
from pathlib import Path

from azure.ai.projects import AIProjectClient
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

    print(f"Using project endpoint: {endpoint}")

    cached_id = load_cached_vector_store_id()

    credential = AzureCliCredential(additionally_allowed_tenants=["*"])
    project_client = AIProjectClient(endpoint=endpoint, credential=credential)

    with project_client.get_openai_client() as openai_client:
        if cached_id:
            try:
                openai_client.vector_stores.retrieve(cached_id)
                print(f"Reusing cached vector store id: {cached_id}")
                return
            except Exception:
                print("Cached vector store not found; creating a new one")

        invoice_dir = Path(__file__).resolve().parents[2] / "data" / "invoices"
        files = sorted(invoice_dir.glob("*.txt"))
        if not files:
            raise ValueError(f"No invoice files found in {invoice_dir}")

        print(f"Found {len(files)} invoice files")
        print("Creating vector store...")
        vector_store = openai_client.vector_stores.create(name="InvoiceVectorStore")
        print(f"Vector store created: {vector_store.id}")

        for i, file_path in enumerate(files, 1):
            print(f"Uploading {i}/{len(files)}: {file_path.name}")
            with open(file_path, "rb") as handle:
                openai_client.vector_stores.files.upload_and_poll(
                    vector_store_id=vector_store.id,
                    file=handle,
                )

    save_vector_store_id(vector_store.id)
    print(f"Vector store ready: {vector_store.id}")


if __name__ == "__main__":
    main()
