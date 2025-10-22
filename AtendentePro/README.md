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

#### 1. **Triage Agent Prompts** (`Triage/triage_prompts.py`)
- **Purpose**: Entry point routing and delegation
- **Structure**: Simple intro with tool usage instructions
- **Key Features**: Delegates to appropriate specialized agents
- **Workflow**: Direct tool-based routing without complex reasoning steps

#### 2. **Flow Agent Prompts** (`Flow/flow_prompts.py`)
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

#### 3. **Interview Agent Prompts** (`Interview/interview_prompts.py`)
- **Purpose**: Structured data collection through guided questions
- **Workflow**: `[READ] → [SUMMARY] → [EXTRACT] → [ANALYZE] → [ROUTE] → [QUESTIONS] → [VERIFY] → [REVIEW] → [OUTPUT INSTRUCTIONS]`
- **Key Features**:
  - **Deep Analysis**: `[ANALYZE]` step identifies what information is still needed
  - **Sequential Questions**: Uses `interview_questions` from configuration
  - **Topic Routing**: Follows `interview_template` for topic routing
  - **One-by-One**: Asks questions sequentially, one at a time
  - **User Interaction**: Waits for user responses before proceeding
- **Important**: Does NOT auto-fill output; requires user interaction first

#### 4. **Answer Agent Prompts** (`Answer/answer_prompts.py`)
- **Purpose**: Generate final recommendations using templates
- **Workflow**: `[READ] → [SUMMARY] → [EXTRACT] → [ANALYZE] → [ROUTE] → [VERIFY] → [REVIEW] → [FORMAT] → [OUTPUT]`
- **Key Features**:
  - **Deep Analysis**: `[ANALYZE]` step analyzes available information and identifies response requirements
  - **Template Integration**: Uses `answer_template` for response guidance
  - **Clear Formatting**: Formats responses clearly and objectively
  - **Validation**: Validates against template requirements
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

## Input Guardrails System

AtendentePro includes a comprehensive, **generic and configurable** input guardrail system that monitors and validates user inputs in real-time, providing security and ensuring appropriate usage across different clients and domains.

### 🏗️ **Architecture Overview**

The guardrail system is designed with **client-specific configurations** that can be easily customized for different businesses:

```
AtendentePro/
├── guardrails.py                    # Generic guardrail functions
├── Template/
│   ├── White_Martins/               # Client-specific configs
│   │   ├── guardrails_config.yaml   # Guardrail rules & topics
│   │   └── agent_guardrails_config.yaml # Agent-to-guardrail mapping
│   └── EasyDr/                      # Another client example
│       └── guardrails_config.yaml
```

### 🔧 **Generic Guardrail Functions**

#### 1. **Content Security** (`reject_sensitive_content`)
- **Purpose**: Blocks sensitive words and suspicious patterns
- **Configuration**: Loads sensitive words from client YAML
- **Protects Against**: Passwords, hacking attempts, malicious code, domain-specific fraud

#### 2. **Topic Validation** (`reject_off_topic_queries`)
- **Purpose**: Ensures queries stay within business scope
- **Configuration**: Loads off-topic keywords from client YAML
- **Blocks**: Cryptocurrency, politics, religion, sports, cooking, etc.

#### 3. **Business Code Validation** (`validate_business_codes`)
- **Purpose**: Validates business-specific codes (IVA, product codes, etc.)
- **Configuration**: Loads valid codes from client YAML
- **Regex Pattern**: `\b([A-Z]\d|[A-Z]{2,3}|\d{2,3})\b`
- **Blocks**: Invalid or non-existent codes

#### 4. **Topic & Code Context Validation** (`validate_topic_and_codes`)
- **Purpose**: Validates codes within specific topic contexts
- **Configuration**: Loads topics with their associated codes and descriptions
- **Advanced Logic**: Ensures codes match the context of the conversation
- **Example**: Code "I0" must be used in "industrialization" context, not "commercialization"

#### 5. **Spam Detection** (`detect_spam_patterns`)
- **Purpose**: Detects spam and repetitive patterns
- **Configuration**: Configurable minimum length and spam patterns
- **Blocks**: Excessive character repetition, very short messages

### 🎯 **Agent-Specific Guardrail Assignment**

Guardrails are dynamically assigned to agents based on `agent_guardrails_config.yaml`:

```yaml
# Example configuration
Triage Agent:
  - reject_off_topic_queries
  - detect_spam_patterns

Flow Agent:
  - reject_off_topic_queries

Interview Agent:
  - reject_sensitive_content

Answer Agent:
  - reject_sensitive_content
  - validate_topic_and_codes  # Only Answer Agent handles codes

Confirmation Agent:
  - reject_sensitive_content

Knowledge Agent:
  - reject_off_topic_queries
  - detect_spam_patterns

Usage Agent:
  - detect_spam_patterns
```

### 📋 **Client Configuration Structure**

#### **guardrails_config.yaml**
```yaml
# Sensitive words and patterns
sensitive_words:
  - "password"
  - "hack"
  - "fraud"

# Off-topic keywords
off_topic_keywords:
  - "bitcoin"
  - "politics"
  - "weather"

# Business topics with codes
topics:
  compra_industrializacao:
    description: "Compra para industrialização"
    codes: ["I0", "ID", "IE", "I8", "I5", "I9", "I2", "I7", "I1", "I3", "I4"]
  
  compra_comercializacao:
    description: "Compra para comercialização"
    codes: ["E0", "ED", "EE", "E8", "E5", "E9", "E2", "E7", "E1", "E3", "E4"]

# All valid codes (consolidated)
valid_codes:
  - "I0"
  - "ID"
  - "E0"
  - "ED"
  # ... etc

# Spam detection settings
min_message_length: 3
spam_patterns: []
```

### 🧪 **Comprehensive Testing**

The system includes extensive test coverage:

```bash
# Run all guardrail tests
python AtendentePro/tests/test_guardrails_comprehensive.py

# Test specific scenarios
python AtendentePro/tests/test_guardrails_topics.py
python AtendentePro/tests/test_guardrails_generic.py
```

**Test Scenarios Covered**:
- ✅ Valid codes in correct contexts
- ✅ Valid codes in wrong contexts (blocked)
- ✅ Invalid/non-existent codes (blocked)
- ✅ Off-topic queries (blocked)
- ✅ Sensitive content (blocked)
- ✅ Spam patterns (blocked)
- ✅ Mixed valid/invalid scenarios
- ✅ Edge cases and boundary conditions

### 🚀 **Usage**

Guardrails run **automatically** in parallel with agent execution:

1. **No Configuration Needed**: Guardrails are integrated into each agent definition
2. **Dynamic Loading**: Configurations are loaded from client-specific YAML files
3. **Real-time Validation**: Inputs are validated before agent processing
4. **Graceful Rejection**: Invalid inputs are blocked with clear error messages

### 🔄 **Multi-Client Support**

The system supports multiple clients with different configurations:

- **White Martins**: IVA codes, energy electricity, industrial/commercial topics
- **EasyDr**: Medical codes, patient data, healthcare topics
- **Custom Clients**: Easy to add new client configurations

### 🛡️ **Security Features**

- **Regex-based Code Detection**: Sophisticated pattern matching for business codes
- **Context Validation**: Ensures codes are used in appropriate contexts
- **Common Word Filtering**: Prevents false positives from common words
- **Case-insensitive Matching**: Handles various input formats
- **Configurable Sensitivity**: Adjustable rules per client needs

---

## Tests

Run the full suite (agent wiring + helpers):

```bash
venv/bin/pytest AtendentePro
```
