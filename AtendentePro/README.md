# AtendentePro

AtendentePro is a multi-agent customer-support workflow built with the OpenAI Agents SDK. The project wires several specialized agents together so they can triage requests, interview users, consult knowledge bases, confirm details, and produce final answers.

- **Tech stack:** Python 3.13+, OpenAI Agents SDK.
- **Entry point:** `AtendentePro/run_env/run.py` launches an interactive console driven by the triage agent.
- **Tests:** `venv/bin/pytest AtendentePro` covers agent wiring and the handoff helper.

---

## 📚 Documentação

### Guias Principais
- **[Setup Guide](../docs/SETUP.md)** - Guia completo de configuração para novos clientes
- **[Architecture](../docs/ARCHITECTURE.md)** - Arquitetura e princípios do sistema

### Documentação por Módulo
- **[Triage Module](../docs/modules/triage.md)** - Sistema de roteamento inteligente
- **[Knowledge Module](../docs/modules/knowledge.md)** - Base de conhecimento e RAG

### Exemplos Práticos
- **[TechStore Configuration](../docs/examples/techstore_config.md)** - Exemplo completo de configuração

---

## Agent Flow

1. **Triage Agent (`Triage/triage_agent.py`)**
   - First responder that routes each conversation.
   - Can hand off to Flow, Confirmation, Knowledge, or Usage agents.

2. **Flow Agent (`Flow/flow_agent.py`)**
   - Intelligently identifies topics from user input using keyword matching.
   - If topic is clearly identified, transfers immediately to Interview Agent.
   - If topic is ambiguous, presents available topics for user selection.
   - Focuses on handoff rather than producing structured output.

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
   - Export environment variable: `export OPENAI_API_KEY="sua-chave-openai"`
   - Or create a `.env` file: `echo "OPENAI_API_KEY=sua-chave-openai" > .env`
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

#### 1. **Flow Agent Prompts** (`Flow/flow_prompts.py`)
- **Purpose**: Intelligent topic identification and automatic handoff
- **Workflow**: `[READ] → [SUMMARY] → [ANALYZE] → [QUESTION] → [VERIFY] → [REVIEW] → [OUTPUT]`
- **Key Features**:
  - **Smart Detection**: `[ANALYZE]` step detects specific topics from user input using `flow_keywords`
  - **Immediate Transfer**: If topic is clearly identified, transfers immediately to Interview Agent
  - **Fallback Presentation**: Only shows topic list when user input is ambiguous
  - **Confirmation Transfer**: When user confirms a topic, transfers immediately to Interview Agent
  - **Keyword Matching**: Uses `flow_keywords` for intelligent topic detection
  - **No Structured Output**: Focuses on handoff rather than producing structured data
- **Behavior**: Direct handoff to Interview Agent without producing FlowOutput

#### 2. **Interview Agent Prompts** (`Interview/interview_prompts.py`)
- **Purpose**: Structured data collection through guided questions
- **Workflow**: `[READ] → [SUMMARY] → [EXTRACT] → [ANALYZE] → [ROUTE] → [QUESTIONS] → [VERIFY] → [REVIEW] → [OUTPUT INSTRUCTIONS]`
- **Key Features**:
  - **Deep Analysis**: `[ANALYZE]` step identifies what information is still needed
  - **Sequential Questions**: Uses `interview_questions` from configuration
  - **Topic Routing**: Follows `interview_template` for topic routing
  - **One-by-One**: Asks questions sequentially, one at a time
  - **User Interaction**: Waits for user responses before proceeding
- **Important**: Does NOT auto-fill output; requires user interaction first

#### 3. **Answer Agent Prompts** (`Answer/answer_prompts.py`)
- **Purpose**: Generate final recommendations using templates
- **Workflow**: `[READ] → [SUMMARY] → [EXTRACT] → [ANALYZE] → [ROUTE] → [VERIFY] → [REVIEW] → [FORMAT] → [OUTPUT]`
- **Key Features**:
  - **Deep Analysis**: `[ANALYZE]` step analyzes available information and identifies response requirements
  - **Template Integration**: Uses `answer_template` for response guidance
  - **Clear Formatting**: Formats responses clearly and objectively
  - **Validation**: Validates against template requirements
- **Output**: Structured answer with topic-specific information

#### 4. **Confirmation Agent Prompts** (`Confirmation/confirmation_prompts.py`)
- **Purpose**: Validate requests and confirm information
- **Workflow**: `[READ] → [SUMMARY] → [EXTRACT] → [CLARIFY] → [CONFIRMATION] → [REVIEW] → [FORMAT] → [ROLLBACK] → [OUTPUT]`
- **Key Features**:
  - Uses `confirmation_template` for validation
  - Includes rollback mechanism for out-of-scope topics
  - References `confirmation_about` for scope definition
  - Falls back to Triage for unrelated topics

#### 5. **Knowledge Agent Prompts** (`Knowledge/knowledge_prompts.py`)
- **Purpose**: RAG-based document retrieval and response
- **Workflow**: `[READ] → [SUMMARY] → [EXTRACT] → [CLARIFY] → [METADATA_DOCUMENTOS] → [RAG] → [REVIEW] → [FORMAT] → [ROLLBACK] → [OUTPUT]`
- **Key Features**:
  - **Document Metadata**: Uses `knowledge_template` for document metadata
  - **RAG Implementation**: Implements RAG with `go_to_rag` function
  - **Source Referencing**: Includes document source referencing
  - **Response Validation**: Validates responses against reference documents
  - **Fallback Handling**: `[ROLLBACK]` step handles cases where information is not found
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
7. **Intelligent Analysis**: `[ANALYZE]` modules provide deep reasoning capabilities

### The `[ANALYZE]` Module

The `[ANALYZE]` step is a key innovation in the prompt architecture that provides intelligent analysis capabilities:

#### **Flow Agent `[ANALYZE]`**
- **Purpose**: Detect specific topics from user input using keywords
- **Function**: Analyzes user message against `flow_keywords` to identify clear topic matches
- **Behavior**: 
  - If topic is clearly identified → Transfer immediately to Interview Agent
  - If topic is ambiguous → Continue to `[QUESTION]` for topic presentation
- **Benefit**: Eliminates unnecessary topic enumeration when user intent is clear

#### **Interview Agent `[ANALYZE]`**
- **Purpose**: Identify what information is still needed for complete understanding
- **Function**: Analyzes available information and determines missing data requirements
- **Behavior**: Guides the agent to ask only necessary questions
- **Benefit**: More efficient interviews with focused questioning

#### **Answer Agent `[ANALYZE]`**
- **Purpose**: Analyze available information and identify response requirements
- **Function**: Deep analysis of collected data to determine appropriate response structure
- **Behavior**: Ensures comprehensive and accurate responses
- **Benefit**: Higher quality answers with better information utilization

#### **Knowledge Agent `[ROLLBACK]`**
- **Purpose**: Handle cases where information is not found in documents
- **Function**: Provides graceful fallback when RAG cannot find relevant information
- **Behavior**: Suggests contacting triage agent for alternative assistance
- **Benefit**: Better user experience with clear guidance when information is unavailable

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

### Testes de Guardrails

```bash
```
