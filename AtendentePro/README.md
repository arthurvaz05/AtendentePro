# AtendentePro

AtendentePro is a multi-agent customer-support workflow built with the OpenAI Agents SDK. The project wires several specialized agents together so they can triage requests, interview users, consult knowledge bases, confirm details, and produce final answers.

- **Tech stack:** Python 3.13+, OpenAI Agents SDK.
- **Entry point:** `AtendentePro/run_env/run.py` launches an interactive console driven by the triage agent.
- **Tests:** `venv/bin/pytest AtendentePro` covers agent wiring and the handoff helper.

---

## Agent Flow

1. **Triage Agent (`Triage/triage_agent.py`)**
   - First responder that routes each conversation.
   - Can hand off to Flow, Confirmation, Knowledge, or Usage agents.

2. **Flow Agent (`Flow/flow_agent.py`)**
   - Determines which interview should run or, if enough data exists, whether to request clarification.
   - Delegates to the Interview agent for structured data collection.

3. **Interview Agent (`Interview/interview_agent.py`)**
   - Collects detailed answers using prompts defined in `Interview/interview_prompts.py`.
   - Produces an `InterviewOutput` object and appends a structured handoff summary for downstream agents.
   - Hands back to Flow (default) or directly to the Answer agent via the network wiring.

4. **Answer Agent (`Answer/answer_agent.py`)**
   - Generates final recommendations using the interview output and templates under `Template/White_Martins/answer_config.py`.
   - Intended as the last stop for customer assistance flows.

5. **Confirmation Agent (`Confirmation/confirmation_agent.py`)**
   - Validates requests before completion; falls back to Triage if the topic is outside its scope.

6. **Knowledge Agent (`Knowledge/knowledge_agent.py`)**
   - Exposes a RAG-style tool (`go_to_rag`) to retrieve information from reference documents.
   - Always falls back to Triage after answering.

7. **Usage Agent (`Usage/usage_agent.py`)**
   - Answers meta-questions about the system itself; falls back to Triage otherwise.

Handoffs are configured centrally in `agent_network.py` and automatically applied via `AtendentePro/__init__.py`.

---

## Agent Hierarchy

```
Triage Agent
├─ Flow Agent
│  ├─ Interview Agent
│  │  └─ Answer Agent
│  └─ (fallback) Triage Agent
├─ Confirmation Agent
│  └─ (fallback) Triage Agent
├─ Knowledge Agent
│  └─ (fallback) Triage Agent
└─ Usage Agent
   └─ (fallback) Triage Agent

Interview Agent (direct fallbacks)
└─ Flow Agent

Answer Agent (fallback)
└─ Interview Agent
```

---

## Project Structure (High-Level)

| Folder / File | Purpose |
| --- | --- |
| `Answer/` | Answer agent, prompts, and structured output model. |
| `Confirmation/` | Confirmation agent and prompts. |
| `Flow/` | Flow agent, keywords, and configuration YAML. |
| `Interview/` | Interview agent, question scripts, and output model. |
| `Knowledge/` | Document-processing utilities and the knowledge agent. |
| `Triage/` | Entry-point triage agent and supporting keyword models. |
| `Usage/` | Usage agent for system guidance. |
| `utils/handoff.py` | Helper to record structured handoff summaries in the shared context and transcript. |
| `context.py` | Defines the shared `ContextNote`, currently just `handoff_summaries`. |
| `agent_network.py` | Central hub that wires agent handoffs and fallback rules. |
| `run_env/run.py` | Interactive CLI runner that starts from the Triage agent. |
| `test_agents_config.py` | Validates agent configuration and network wiring. |
| `test_handoff_utils.py` | Tests the handoff summary helper. |

---

## Template Structure (Client-Specific)

All customer customizations live under `Template/`. Each new deployment should update these files while the rest of the codebase remains unchanged.

| Template File / Folder | Customize for each client? | Description |
| --- | --- | --- |
| `Template/White_Martins/answer_config.yaml` | ✅ | Defines answer topics, descriptions, and allowed IVA codes. |
| `Template/White_Martins/answer_config.py` | ✅ | Loads the YAML into models; only adjust if the YAML schema changes. |
| `Template/White_Martins/confirmation_config.yaml` | ✅ | Provides confirmation text, formats, and business rules. |
| `Template/White_Martins/flow_config.yaml` | ✅ | Lists flow topics and keyword mappings used by the Flow agent. |
| `Template/White_Martins/interview_config.yaml` | ✅ | Interview questions and flow for each topic. |
| `Template/White_Martins/knowledge_config.yaml` | ✅ | Describes the knowledge base metadata (document descriptions, usage hints). |
| `Template/White_Martins/knowledge_documentos/` | ✅ | Client documents plus generated embeddings and JSON chunks. Replace with the customer's materials. |
| `Template/White_Martins/triage_config.yaml` | ✅ | Keywords for mapping user intents to Flow/Confirmation/Knowledge/Usage agents. |
| `Answer/answer_models.py` | ✅ | Enum of answer topics; extend/rename values to match the client's taxonomy. |

---

## Running Locally

1. **Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt  # or sync with pyproject if present
   ```
2. **Configure your model provider**
   - For Azure OpenAI: set `OPENAI_PROVIDER=azure` and export `AZURE_API_KEY`, `AZURE_API_ENDPOINT`, `AZURE_API_VERSION` (optionally `AZURE_DEPLOYMENT_NAME`).
   - For OpenAI public API: set `OPENAI_PROVIDER=openai` and export `OPENAI_API_KEY`.
3. **Launch the triage loop**
   ```bash
   python -m AtendentePro.run_env.run
   ```
   or choose another agent:
   ```bash
   python -m AtendentePro.run_env.run flow
   python -m AtendentePro.run_env.run knowledge
   python -m AtendentePro.run_env.run triage
   ```


## Tests

Run the full suite (agent wiring + helpers):

```bash
venv/bin/pytest AtendentePro
```

---

## Debugging in VS Code

This repository includes a `.vscode/launch.json` with two helpful configurations:

- "Python: Debug Current File": Run and debug the currently open Python file in the integrated terminal. It sets `PYTHONPATH` to the workspace root so imports like `AtendentePro.*` work.
- "Run AtendentePro (choose agent)": Launch the main CLI runner module `AtendentePro.run_env.run` and pick which agent to start (triage, flow, interview, answer, confirmation, knowledge, usage).

To use: open the file you want to debug, then select the "Python: Debug Current File" configuration and start the debugger. Or choose the second configuration and select the agent using the prompt.
