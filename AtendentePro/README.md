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
2. **Set your OpenAI key**
   - Edit `AtendentePro/config.py` or export `OPENAI_API_KEY`.
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

---

## Prompt Modules Architecture

Each agent in AtendentePro uses a structured prompt system with modular components. These prompts define the agent's behavior, reasoning process, and interaction patterns.

### Prompt Structure Pattern

All prompt modules follow a consistent structure:
- **INTRO**: Agent role and primary objective
- **MODULES**: Sequential workflow steps (internal reasoning)
- **Step Modules**: Individual processing steps (READ, SUMMARY, EXTRACT, etc.)
- **Combined Prompt**: Final concatenated instruction set

### Agent Prompt Modules

#### 1. **Triage Agent Prompts** (`Triage/triage_prompts.py`)
- **Purpose**: Entry point routing and delegation
- **Structure**: Simple intro with tool usage instructions
- **Key Features**: Delegates to appropriate specialized agents
- **Workflow**: Direct tool-based routing without complex reasoning steps

#### 2. **Flow Agent Prompts** (`Flow/flow_prompts.py`)
- **Purpose**: Topic identification and user confirmation
- **Workflow**: `[READ] → [SUMMARY] → [QUESTION] → [VERIFY] → [REVIEW] → [OUTPUT]`
- **Key Features**:
  - Presents available topics from `flow_template`
  - Requires explicit user confirmation
  - Uses `flow_keywords` for topic matching
  - Validates user responses before proceeding
- **Output**: `FlowOutput` with selected topic and reasoning

#### 3. **Interview Agent Prompts** (`Interview/interview_prompts.py`)
- **Purpose**: Structured data collection through guided questions
- **Workflow**: `[READ] → [SUMMARY] → [EXTRACT] → [ROUTE] → [VERIFY] → [REVIEW] → [QUESTIONS]`
- **Key Features**:
  - Uses `interview_questions` from configuration
  - Follows `interview_template` for topic routing
  - Asks questions sequentially, one at a time
  - Waits for user responses before proceeding
- **Important**: Does NOT auto-fill output; requires user interaction first

#### 4. **Answer Agent Prompts** (`Answer/answer_prompts.py`)
- **Purpose**: Generate final recommendations using templates
- **Workflow**: `[READ] → [SUMMARY] → [EXTRACT] → [ROUTE] → [VERIFY] → [REVIEW] → [FORMAT] → [OUTPUT]`
- **Key Features**:
  - Uses `answer_template` for response guidance
  - Formats responses clearly and objectively
  - Validates against template requirements
- **Output**: Structured answer with topic-specific information

#### 5. **Confirmation Agent Prompts** (`Confirmation/confirmation_prompts.py`)
- **Purpose**: Validate requests and confirm information
- **Workflow**: `[READ] → [SUMMARY] → [EXTRACT] → [CLARIFY] → [CONFIRMATION] → [REVIEW] → [FORMAT] → [ROLLBACK] → [OUTPUT]`
- **Key Features**:
  - Uses `confirmation_template` for validation
  - Includes rollback mechanism for out-of-scope topics
  - References `confirmation_about` for scope definition
  - Falls back to Triage for unrelated topics

#### 6. **Knowledge Agent Prompts** (`Knowledge/knowledge_prompts.py`)
- **Purpose**: RAG-based document retrieval and response
- **Workflow**: `[READ] → [SUMMARY] → [EXTRACT] → [CLARIFY] → [METADATA_DOCUMENTOS] → [RAG] → [REVIEW] → [FORMAT] → [ROLLBACK] → [OUTPUT]`
- **Key Features**:
  - Uses `knowledge_template` for document metadata
  - Implements RAG with `go_to_rag` function
  - Includes document source referencing
  - Validates responses against reference documents
- **RAG Process**: Combines document context with user question

#### 7. **Usage Agent Prompts** (`Usage/usage_agent.py`)
- **Purpose**: System guidance and meta-questions
- **Structure**: Simple instruction-based approach
- **Key Features**: Answers questions about system usage and functionality

### Prompt Design Principles

1. **Modularity**: Each step is clearly defined and reusable
2. **Internal Reasoning**: All processing steps are marked as internal reasoning
3. **User Interaction**: Clear separation between internal processing and user communication
4. **Validation**: Multiple verification steps ensure accuracy
5. **Fallback Mechanisms**: Rollback options for out-of-scope requests
6. **Template Integration**: Prompts dynamically incorporate configuration templates

### Configuration Integration

Prompts are dynamically enhanced with:
- **Templates**: From YAML configuration files
- **Keywords**: For topic matching and routing
- **Questions**: Structured interview scripts
- **Metadata**: Document descriptions and usage hints

This architecture ensures consistent behavior while allowing client-specific customization through the Template system.

---

## Tests

Run the full suite (agent wiring + helpers):

```bash
venv/bin/pytest AtendentePro
```
