import json
import os
import sys
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    FileSearchTool,
    PromptAgentDefinition,
    PromptAgentDefinitionText,
    ResponseTextFormatConfigurationJsonSchema,
)
from azure.identity import AzureCliCredential
from dotenv import load_dotenv


def load_env() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)


def load_vector_store_id() -> str:
    cache_path = Path(__file__).resolve().parents[1] / ".foundry" / "vector_store.json"
    if not cache_path.exists():
        raise FileNotFoundError(
            "Vector store id not found. Run: python src/index_invoices.py"
        )
    data = json.loads(cache_path.read_text())
    return data["vector_store_id"]


def load_schema() -> dict:
    schema_path = Path(__file__).resolve().parent / "schema.json"
    return json.loads(schema_path.read_text())


def load_agent_cache() -> dict | None:
    agent_path = Path(__file__).resolve().parents[1] / ".foundry" / "agent.json"
    if not agent_path.exists():
        return None
    return json.loads(agent_path.read_text())


def save_agent_cache(agent_name: str, agent_version: str, vector_store_id: str) -> None:
    output_dir = Path(__file__).resolve().parents[1] / ".foundry"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "agent.json"
    output_path.write_text(
        json.dumps(
            {
                "agent_name": agent_name,
                "agent_version": agent_version,
                "vector_store_id": vector_store_id,
            },
            indent=2,
        )
    )


def main() -> None:
    load_env()

    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT") or os.environ.get(
        "FOUNDRY_PROJECT_ENDPOINT"
    )
    model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME")
    agent_name = os.environ.get("AZURE_AI_AGENT_NAME", "invoice-assistant-v2")

    if not endpoint:
        raise ValueError("AZURE_AI_PROJECT_ENDPOINT is required")
    if not model:
        raise ValueError("AZURE_AI_MODEL_DEPLOYMENT_NAME is required")

    print(f"Using project endpoint: {endpoint}")
    print(f"Model: {model}")
    print(f"Agent name: {agent_name}")

    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise ValueError("Provide a question as a command-line argument")

    vector_store_id = load_vector_store_id()
    schema = load_schema()
    print(f"Using vector store: {vector_store_id}")

    credential = AzureCliCredential(additionally_allowed_tenants=["*"])
    project_client = AIProjectClient(endpoint=endpoint, credential=credential)

    instructions = (
        "You are an invoice assistant. Use the File Search tool to answer questions. "
        f"Always return your response as valid JSON matching this schema: {json.dumps(schema)}. "
        "Include answer and top_documents array with doc_id, file_name, and snippet for each document."
    )

    file_search = FileSearchTool(vector_store_ids=[vector_store_id])

    with project_client.get_openai_client() as openai_client:
        agent_cache = load_agent_cache()
        agent_version = None

        if agent_cache:
            if agent_cache.get("vector_store_id") == vector_store_id:
                agent_version = agent_cache.get("agent_version")
                agent_name = agent_cache.get("agent_name", agent_name)

        if not agent_version:
            agent = project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions=instructions,
                    tools=[file_search],
                    text=PromptAgentDefinitionText(
                        format=ResponseTextFormatConfigurationJsonSchema(
                            name="InvoiceAnswer",
                            schema=schema,
                            description="Answer invoice questions with citations.",
                        )
                    ),
                ),
            )
            agent_version = agent.version
            save_agent_cache(agent.name, agent.version, vector_store_id)
            print(f"✓ Agent created: {agent.name} (version {agent.version})")
        else:
            print(f"Reusing agent: {agent_name} (version {agent_version})")

        conversation = openai_client.conversations.create(
            items=[{"type": "message", "role": "user", "content": question}]
        )

        response = openai_client.responses.create(
            conversation=conversation.id,
            input="",
            extra_body={"agent": {"name": agent_name, "type": "agent_reference"}},
        )

        print(response.output_text)


if __name__ == "__main__":
    main()
