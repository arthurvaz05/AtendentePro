# 🚀 Guia de Configuração - AtendentePro

## 📋 Visão Geral

O AtendentePro é um sistema de agentes especializados com arquitetura modular e sistema de templates inteligente. Este guia mostra como configurar o sistema para novos clientes.

## 🏗️ Arquitetura do Sistema

```
AtendentePro/
├── 📁 Agent Modules (Genéricos)
│   ├── Triage/          # Roteamento inteligente
│   ├── Answer/          # Respostas técnicas
│   ├── Knowledge/       # Base de conhecimento
│   └── ...              # Outros agentes
│
├── 📁 Template System
│   ├── Template/        # Templates genéricos (DEFAULT)
│   └── Template/[CLIENTE]/ # Configurações específicas
│
└── 📁 Core System
    ├── guardrails.py    # Sistema de guardrails
    ├── config.py        # Configuração principal
    └── agent_network.py # Rede de agentes
```

## 🎯 Passo a Passo para Novo Cliente

### 1. Criar Pasta do Cliente

```bash
mkdir AtendentePro/Template/[NOME_DO_CLIENTE]
```

**Exemplo:**
```bash
mkdir AtendentePro/Template/Acme_Corp
```

### 2. Configurar Sistema de Guardrails

Criar `AtendentePro/Template/[CLIENTE]/guardrails_config.yaml`:

```yaml
agent_scopes:
  triage_agent:
    about: |
      O Triage Agent da [NOME_CLIENTE] é responsável por [DESCRIÇÃO_DO_DOMÍNIO].
      Ele deve reconhecer perguntas sobre: [TÓPICOS_ESPECÍFICOS].
      Não deve responder sobre [TÓPICOS_FORA_DO_ESCOPO].
  
  answer_agent:
    about: |
      O Answer Agent da [NOME_CLIENTE] fornece [TIPO_DE_RESPOSTAS].
      Especializado em [DOMÍNIO_ESPECÍFICO].
      Não deve responder sobre [LIMITAÇÕES].
  
  # ... outros agentes
```

### 3. Configurar Sistema de Triage

Criar `AtendentePro/Template/[CLIENTE]/triage_config.yaml`:

```yaml
agent_keywords:
  answer_agent:
    keywords:
      - "palavra-chave-1"
      - "palavra-chave-2"
      - "termo-específico"
    description: "Descrição do que este agente faz"
  
  knowledge_agent:
    keywords:
      - "documento"
      - "manual"
      - "procedimento"
    description: "Acessa base de conhecimento"
  
  # ... outros agentes

routing_rules:
  priority_order:
    - "answer_agent"
    - "knowledge_agent"
    - "confirmation_agent"
    - "interview_agent"
    - "flow_agent"
    - "usage_agent"
  default_agent: "knowledge_agent"
```

### 4. Configurar Agentes Específicos

Para cada agente, criar arquivos de configuração:

#### Answer Agent
```yaml
# AtendentePro/Template/[CLIENTE]/answer_config.yaml
agent_name: "Answer Agent"
description: "Fornece respostas técnicas sobre [DOMÍNIO]"
instructions: |
  Você é um especialista em [DOMÍNIO_ESPECÍFICO].
  Suas responsabilidades incluem:
  - [RESPONSABILIDADE_1]
  - [RESPONSABILIDADE_2]
  
  Não responda sobre:
  - [LIMITAÇÃO_1]
  - [LIMITAÇÃO_2]
```

#### Knowledge Agent
```yaml
# AtendentePro/Template/[CLIENTE]/knowledge_config.yaml
agent_name: "Knowledge Agent"
description: "Acessa base de conhecimento sobre [DOMÍNIO]"
rag_config:
  documents_path: "knowledge_documentos/"
  embedding_model: "text-embedding-ada-002"
  max_results: 5
```

### 5. Configurar Base de Conhecimento (Opcional)

Se usar Knowledge Agent:

```bash
mkdir AtendentePro/Template/[CLIENTE]/knowledge_documentos
mkdir AtendentePro/Template/[CLIENTE]/knowledge_documentos/json_format
mkdir AtendentePro/Template/[CLIENTE]/knowledge_documentos/embedding
```

Adicionar documentos na pasta `knowledge_documentos/`.

### 6. Configurar Variáveis de Ambiente

Criar `.env` na raiz do projeto:

```bash
OPENAI_API_KEY=sk-proj-sua-chave-aqui
```

### 7. Testar Configuração

```bash
# Testar sistema de guardrails
echo "pergunta fora do escopo" | python -m AtendentePro.run_env.run triage

# Testar agente específico
echo "pergunta relevante" | python -m AtendentePro.run_env.run answer
```

## 🔧 Configurações Avançadas

### Personalização de Prompts

Os prompts são construídos dinamicamente usando:
- `guardrails_config.yaml` para escopo
- `triage_config.yaml` para roteamento
- `*_config.yaml` para cada agente

### Fallback Inteligente

O sistema busca configurações na seguinte ordem:
1. `Template/[CLIENTE]/` (específico)
2. `Template/` (genérico)
3. Raiz do projeto (fallback)

### Sistema de Guardrails

O sistema de guardrails funciona automaticamente:
- Detecta mensagens fora do escopo
- Aplica rollback educado
- Mantém foco no domínio configurado

## 📚 Exemplos Práticos

### Exemplo 1: Cliente de E-commerce

```yaml
# guardrails_config.yaml
agent_scopes:
  triage_agent:
    about: |
      O Triage Agent da TechStore é responsável por atendimento ao cliente.
      Especializado em: produtos, pedidos, devoluções, garantias.
      Não responde sobre: programação, matemática, assuntos pessoais.
```

### Exemplo 2: Cliente de Saúde

```yaml
# guardrails_config.yaml
agent_scopes:
  triage_agent:
    about: |
      O Triage Agent da MedClinic é responsável por triagem médica.
      Especializado em: sintomas, agendamentos, medicamentos.
      Não responde sobre: diagnósticos específicos, emergências.
```

## 🚨 Troubleshooting

### Problema: Sistema não encontra configurações
**Solução:** Verificar se a pasta do cliente está em `Template/[CLIENTE]/`

### Problema: Guardrails não funcionam
**Solução:** Verificar se `guardrails_config.yaml` tem seção `agent_scopes`

### Problema: Triage não roteia corretamente
**Solução:** Verificar se `triage_config.yaml` tem `agent_keywords` e `routing_rules`

## 📞 Suporte

Para dúvidas sobre configuração:
1. Verificar documentação específica em `docs/modules/`
2. Consultar exemplos em `docs/examples/`
3. Testar com configurações da White Martins como referência

---

**Próximos Passos:**
- [ ] Configurar agente específico
- [ ] Testar sistema de guardrails
- [ ] Adicionar documentos à base de conhecimento
- [ ] Executar testes automatizados
