import json
import os
import sys
from pathlib import Path

from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from dotenv import load_dotenv


def load_env() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)


def build_client() -> AzureOpenAI:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
    if not endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT is required")
    print(f"Using endpoint: {endpoint}")
    print(f"Using API version: {api_version}")

    credential = DefaultAzureCredential()

    def token_provider() -> str:
        return credential.get_token(
            "https://cognitiveservices.azure.com/.default"
        ).token

    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_version=api_version,
        azure_ad_token_provider=token_provider,
    )


def load_vector_store_id() -> str:
    vector_path = Path(__file__).resolve().parents[1] / ".aoai" / "vector_store.json"
    if not vector_path.exists():
        raise FileNotFoundError(
            "Vector store id not found. Run: python src/index_invoices.py"
        )
    data = json.loads(vector_path.read_text())
    return data["vector_store_id"]


def load_schema() -> dict:
    schema_path = Path(__file__).resolve().parent / "schema.json"
    return json.loads(schema_path.read_text())


def main() -> None:
    load_env()

    model = os.environ.get("MODEL_DEPLOYMENT_NAME")
    if not model:
        raise ValueError("MODEL_DEPLOYMENT_NAME is required")

    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise ValueError("Provide a question as a command-line argument")

    print("Starting Responses API query...")
    client = build_client()
    vector_store_id = load_vector_store_id()
    schema = load_schema()
    print(f"Using vector store: {vector_store_id}")
    print(f"Model: {model}")

    print("Sending request...")
    response = client.responses.create(
        model=model,
        input=[{"role": "user", "content": question}],
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [vector_store_id],
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "InvoiceAnswer",
                "schema": schema,
                "strict": True,
            }
        },
    )
    print("Response received")

    output_text = None
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            if getattr(content, "type", None) == "output_text":
                output_text = content.text
                break
        if output_text:
            break

    if not output_text:
        raise RuntimeError("No output_text found in response")

    print(output_text)


if __name__ == "__main__":
    main()
