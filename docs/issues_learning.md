# Issues and Learnings (Foundry Agent SDK Demo)

This document captures issues and learnings while upgrading `agents_v2_responses` from
`azure-ai-projects==2.0.0b3` to `azure-ai-projects==2.0.0b4`, with a focus on structured
JSON output behavior.

For each issue: symptom, root cause, fix applied, and reusable learning.

## 1) b4 SDK import and payload breaking changes

Permalink: 1) b4 SDK import and payload breaking changes

- Symptom:
  - Runtime failed after upgrade with:
    - `ImportError: cannot import name 'ResponseTextFormatConfigurationJsonSchema'`
  - Agent invocation payload in `responses.create(...)` was still using:
    - `extra_body={"agent": {...}}`
- Root cause:
  - `azure-ai-projects==2.0.0b4` introduced breaking changes in model/type names and
    agent invocation payload shape.
  - Structured text option class names changed compared to b3-era code.
  - Agent reference key changed from `agent` to `agent_reference`.
- Fix:
  - Updated dependency pin to `azure-ai-projects==2.0.0b4`.
  - Updated imports and usage in `agents_v2_responses/src/run_agent.py`:
    - `PromptAgentDefinitionText` -> `PromptAgentDefinitionTextOptions`
    - `ResponseTextFormatConfigurationJsonSchema` -> `TextResponseFormatJsonSchema`
  - Updated response call payload:
    - `extra_body={"agent_reference": {"name": agent_name, "type": "agent_reference"}}`
- Learning:
  - For preview SDK upgrades, always read release-history breaking changes before testing
    runtime behavior.
  - Type renames and request payload-key changes can silently block otherwise-correct
    business logic.

## 2) Layer clarity: agentic definition vs inference execution (including streaming)

Permalink: 2) Layer clarity: agentic definition vs inference execution (including streaming)

- Symptom:
  - Confusion about where JSON and streaming are controlled:
    - agent definition (`create_version`) vs
    - OpenAI Responses call (`responses.create` / `responses.stream`).
- Root cause:
  - Both APIs are used in the same script, but they serve different lifecycles.
  - The script previously used only non-stream inference, so streaming ownership was not explicit.
- Fix:
  - Confirmed and documented separation of responsibilities:
    - Agentic layer (`project_client.agents.create_version(...)`) defines instructions,
      tools, and output schema contract (`TextResponseFormatJsonSchema`).
    - Inference layer (`openai_client.responses...`) executes a turn and returns output.
  - Added streaming inference mode to `agents_v2_responses/src/run_agent.py` via `--stream`.
  - Implemented `responses.stream(...)` path and validated output remains schema-shaped JSON.
  - Streaming path required explicit `model` parameter with current SDK combination.
- Learning:
  - JSON schema definition belongs to the agentic configuration layer.
  - Runtime mode (sync vs streaming) belongs to the inference layer.
  - Skipping the inference call means the agent is defined but no answer is generated.
  - This same layering model applies to both `2.0.0b3` and `2.0.0b4`.

## Current snapshot (validated)

- Dependency:
  - `agents_v2_responses/requirements.txt` now pins `azure-ai-projects==2.0.0b4`.
- Code compatibility:
  - `agents_v2_responses/src/run_agent.py` updated for b4 class names and `agent_reference` payload.
- Tests:
  - `pytest -q` -> `2 passed`.
- Live run:
  - `python3 src/run_agent.py "What is the total due on invoice INV-1002?"`
  - Returned JSON string directly from agent response.
- JSON parse check:
  - Parsed output with `json.loads(...)` and validated keys.
  - Result: `JSON_OK ['answer', 'top_documents']`.
- Streaming run:
  - `python3 src/run_agent.py --stream "What is the total due on invoice INV-1002?"`
  - Streaming inference completed and emitted final JSON output.
- Streaming JSON parse check:
  - Parsed streamed output and validated keys.
  - Result: `STREAM_JSON_OK ['answer', 'top_documents']`.
