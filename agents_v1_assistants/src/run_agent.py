import json
import os
import sys
from pathlib import Path

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    FileSearchTool,
    ResponseFormatJsonSchema,
    ResponseFormatJsonSchemaType,
)
from azure.identity import AzureCliCredential
from dotenv import load_dotenv


def load_vector_store_id() -> str:
    vector_path = Path(__file__).resolve().parents[1] / ".foundry" / "vector_store.json"
    if not vector_path.exists():
        raise FileNotFoundError(
            "Vector store id not found. Run: python src/index_invoices.py"
        )
    data = json.loads(vector_path.read_text())
    return data["vector_store_id"]


def load_schema() -> dict:
    schema_path = Path(__file__).resolve().parent / "schema.json"
    return json.loads(schema_path.read_text())


def load_agent_cache() -> dict | None:
    agent_path = Path(__file__).resolve().parents[1] / ".foundry" / "agent.json"
    if not agent_path.exists():
        return None
    return json.loads(agent_path.read_text())


def save_agent_cache(agent_id: str, vector_store_id: str) -> None:
    output_dir = Path(__file__).resolve().parents[1] / ".foundry"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "agent.json"
    output_path.write_text(
        json.dumps(
            {"agent_id": agent_id, "vector_store_id": vector_store_id}, indent=2
        )
    )


def main() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)

    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT") or os.environ.get(
        "FOUNDRY_PROJECT_ENDPOINT"
    )
    model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME") or os.environ.get(
        "MODEL_DEPLOYMENT_NAME"
    )

    if not endpoint:
        raise ValueError("AZURE_AI_PROJECT_ENDPOINT is required")
    if not model:
        raise ValueError("AZURE_AI_MODEL_DEPLOYMENT_NAME is required")

    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise ValueError("Provide a question as a command-line argument")

    vector_store_id = load_vector_store_id()
    schema = load_schema()

    credential = AzureCliCredential(additionally_allowed_tenants=["*"])
    agents_client = AgentsClient(endpoint=endpoint, credential=credential)

    instructions = (
        "You are an invoice assistant. Use the File Search tool to answer questions. "
        f"Always return your response as valid JSON matching this schema: {json.dumps(schema)}. "
        "Include answer and top_documents array with doc_id, file_name, and snippet for each document."
    )

    print(f"Using vector store: {vector_store_id}")
    print(f"Model: {model}\n")

    try:
        file_search = FileSearchTool(vector_store_ids=[vector_store_id])

        agent_cache = load_agent_cache()
        agent_id = None
        if agent_cache:
            if agent_cache.get("vector_store_id") == vector_store_id:
                agent_id = agent_cache.get("agent_id")
        agent = None
        if agent_id:
            try:
                agent = agents_client.get_agent(agent_id)
                print(f"Reusing agent: {agent.id}")
            except Exception:
                agent = None

        if agent is None:
            print("Creating agent...")
            agent = agents_client.create_agent(
                model=model,
                name="invoice-assistant",
                instructions=instructions,
                tools=file_search.definitions,
                tool_resources=file_search.resources,
                response_format=ResponseFormatJsonSchemaType(
                    json_schema=ResponseFormatJsonSchema(
                        name="InvoiceAnswer",
                        schema=schema,
                        description="Answer invoice questions with citations.",
                    )
                ),
            )
            save_agent_cache(agent.id, vector_store_id)
            print(f"✓ Agent created: {agent.id}")

        thread = agents_client.threads.create()
        print(f"✓ Thread created: {thread.id}")

        agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content=question,
        )

        print("Running agent...")
        run = agents_client.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id,
        )
        print(f"✓ Run completed with status: {run.status}\n")

        status_value = getattr(run.status, "value", str(run.status))
        if str(status_value).lower() == "completed":
            messages = agents_client.messages.list(thread_id=thread.id)
            print("=" * 80)
            print("ASSISTANT RESPONSE:")
            print("=" * 80)
            for message in messages:
                if message.role == "assistant":
                    content = message.content
                    if content and hasattr(content[0], "text"):
                        print(content[0].text.value)
                    break
            print("=" * 80)
        else:
            print(f"⚠ Run did not complete successfully: {run.status}")
            if hasattr(run, "last_error"):
                print(f"Error: {run.last_error}")

        # agents_client.threads.delete(thread.id)
        # print("\n✓ Thread deleted")
        # agents_client.delete_agent(agent.id)
        # print("✓ Agent deleted")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
