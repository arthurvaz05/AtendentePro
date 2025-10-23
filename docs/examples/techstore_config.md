# 📝 Exemplo Prático - Configuração para Cliente "TechStore"

Este exemplo mostra como configurar o AtendentePro para um cliente fictício de e-commerce chamado "TechStore".

## 🎯 Perfil do Cliente

**TechStore** é uma loja online de produtos eletrônicos que precisa de:
- Atendimento ao cliente sobre produtos
- Suporte técnico
- Informações sobre pedidos e devoluções
- Orientações sobre garantias

## 📁 Estrutura de Arquivos

```
AtendentePro/Template/TechStore/
├── guardrails_config.yaml
├── triage_config.yaml
├── answer_config.yaml
├── knowledge_config.yaml
├── confirmation_config.yaml
├── interview_config.yaml
├── flow_config.yaml
└── knowledge_documentos/
    ├── produtos/
    ├── garantias/
    ├── devolucoes/
    └── suporte_tecnico/
```

## ⚙️ Configurações

### 1. Guardrails Configuration

```yaml
# AtendentePro/Template/TechStore/guardrails_config.yaml
agent_scopes:
  triage_agent:
    about: |
      O Triage Agent da TechStore é responsável por atendimento ao cliente de e-commerce.
      Ele deve reconhecer perguntas sobre: produtos eletrônicos, pedidos, devoluções, 
      garantias, suporte técnico, políticas da loja, métodos de pagamento e entrega.
      Não deve responder sobre: programação, matemática avançada, assuntos pessoais,
      produtos de concorrentes, questões médicas ou jurídicas.
  
  answer_agent:
    about: |
      O Answer Agent da TechStore fornece respostas técnicas sobre produtos eletrônicos.
      Especializado em: especificações técnicas, compatibilidade, troubleshooting básico,
      recomendações de produtos, comparações técnicas.
      Não deve responder sobre: diagnósticos médicos, questões jurídicas, 
      produtos de outras marcas não vendidas pela TechStore.
  
  knowledge_agent:
    about: |
      O Knowledge Agent da TechStore acessa a base de conhecimento da empresa.
      Especializado em: políticas da loja, procedimentos de devolução, garantias,
      métodos de pagamento, prazos de entrega, termos de uso.
      Não deve responder sobre: especificações técnicas detalhadas, troubleshooting avançado.
  
  confirmation_agent:
    about: |
      O Confirmation Agent da TechStore confirma informações sobre pedidos e transações.
      Especializado em: status de pedidos, confirmações de pagamento, agendamentos,
      validações de garantia, confirmações de devolução.
      Não deve responder sobre: informações técnicas de produtos, políticas gerais.
  
  interview_agent:
    about: |
      O Interview Agent da TechStore coleta informações para suporte personalizado.
      Especializado em: coleta de dados do cliente, histórico de pedidos,
      problemas específicos, necessidades de produtos.
      Não deve responder sobre: diagnósticos técnicos, informações confidenciais.
  
  flow_agent:
    about: |
      O Flow Agent da TechStore gerencia fluxos de atendimento e processos.
      Especializado em: processos de devolução, fluxos de garantia, etapas de pedido,
      procedimentos de suporte técnico.
      Não deve responder sobre: informações específicas de produtos, dados pessoais.
  
  usage_agent:
    about: |
      O Usage Agent da TechStore orienta sobre o uso do sistema de atendimento.
      Especializado em: navegação no site, uso do chat, funcionalidades da conta,
      tutoriais de compra.
      Não deve responder sobre: informações de produtos, políticas da empresa.
```

### 2. Triage Configuration

```yaml
# AtendentePro/Template/TechStore/triage_config.yaml
agent_keywords:
  answer_agent:
    keywords:
      - "especificação técnica"
      - "compatibilidade"
      - "troubleshooting"
      - "recomendação"
      - "comparação"
      - "qualidade"
      - "performance"
      - "características"
      - "funcionalidades"
      - "técnico"
    description: "Respostas técnicas sobre produtos eletrônicos"
  
  knowledge_agent:
    keywords:
      - "política"
      - "devolução"
      - "garantia"
      - "pagamento"
      - "entrega"
      - "prazo"
      - "termos"
      - "condições"
      - "procedimento"
      - "regulamento"
    description: "Informações sobre políticas e procedimentos da TechStore"
  
  confirmation_agent:
    keywords:
      - "status pedido"
      - "confirmação"
      - "pagamento"
      - "agendamento"
      - "validação"
      - "verificar"
      - "confirmar"
      - "pedido"
      - "transação"
      - "compra"
    description: "Confirmações sobre pedidos e transações"
  
  interview_agent:
    keywords:
      - "coletar informações"
      - "histórico"
      - "problema específico"
      - "necessidade"
      - "preferência"
      - "entrevista"
      - "questionário"
      - "dados cliente"
      - "perfil"
      - "personalização"
    description: "Coleta de informações para suporte personalizado"
  
  flow_agent:
    keywords:
      - "processo devolução"
      - "fluxo garantia"
      - "etapas pedido"
      - "procedimento"
      - "workflow"
      - "processo"
      - "etapa"
      - "sequência"
      - "passo a passo"
      - "roteiro"
    description: "Gerenciamento de fluxos e processos"
  
  usage_agent:
    keywords:
      - "como usar"
      - "navegação"
      - "tutorial"
      - "ajuda"
      - "orientação"
      - "funcionalidade"
      - "conta"
      - "login"
      - "cadastro"
      - "sistema"
    description: "Orientações sobre uso do sistema"

routing_rules:
  priority_order:
    - "confirmation_agent"  # Pedidos têm prioridade
    - "answer_agent"        # Suporte técnico em segundo
    - "knowledge_agent"     # Políticas em terceiro
    - "interview_agent"     # Coleta de dados em quarto
    - "flow_agent"          # Processos em quinto
    - "usage_agent"         # Uso do sistema por último
  default_agent: "knowledge_agent"
```

### 3. Answer Agent Configuration

```yaml
# AtendentePro/Template/TechStore/answer_config.yaml
agent_name: "Answer Agent"
description: "Fornece respostas técnicas sobre produtos eletrônicos da TechStore"

instructions: |
  Você é um especialista em produtos eletrônicos da TechStore.
  
  Suas responsabilidades incluem:
  - Fornecer especificações técnicas detalhadas
  - Explicar compatibilidade entre produtos
  - Oferecer troubleshooting básico
  - Recomendar produtos baseado em necessidades
  - Comparar características técnicas
  
  Sempre:
  - Cite fontes oficiais quando possível
  - Seja preciso com especificações técnicas
  - Ofereça alternativas quando apropriado
  - Mantenha tom profissional e prestativo
  
  Não responda sobre:
  - Produtos de concorrentes
  - Questões médicas ou jurídicas
  - Troubleshooting avançado que requer técnico especializado
  - Informações confidenciais da empresa

product_categories:
  - "smartphones"
  - "laptops"
  - "tablets"
  - "acessorios"
  - "gaming"
  - "audio"
  - "fotografia"

response_format:
  include_specifications: true
  include_compatibility: true
  include_alternatives: true
  max_response_length: 500
```

### 4. Knowledge Agent Configuration

```yaml
# AtendentePro/Template/TechStore/knowledge_config.yaml
agent_name: "Knowledge Agent"
description: "Acessa base de conhecimento sobre políticas e procedimentos da TechStore"

rag_config:
  documents_path: "knowledge_documentos/"
  embedding_model: "text-embedding-ada-002"
  max_results: 5
  similarity_threshold: 0.7
  
document_categories:
  - "politicas_devolucao"
  - "garantias"
  - "metodos_pagamento"
  - "prazos_entrega"
  - "termos_uso"
  - "politica_privacidade"
  - "suporte_tecnico"

response_format:
  include_sources: true
  citation_style: "numbered"
  max_context_length: 2000
```

## 🧪 Testes de Configuração

### Teste 1: Pergunta Técnica
```bash
echo "Qual a diferença entre SSD e HDD?" | python -m AtendentePro.run_env.run triage
# Esperado: Redirecionar para Answer Agent
```

### Teste 2: Pergunta sobre Política
```bash
echo "Qual o prazo para devolução?" | python -m AtendentePro.run_env.run triage
# Esperado: Redirecionar para Knowledge Agent
```

### Teste 3: Confirmação de Pedido
```bash
echo "Quero confirmar o status do meu pedido" | python -m AtendentePro.run_env.run triage
# Esperado: Redirecionar para Confirmation Agent
```

### Teste 4: Pergunta Fora do Escopo
```bash
echo "Como fazer um bolo de chocolate?" | python -m AtendentePro.run_env.run triage
# Esperado: Rollback educado pelo sistema de guardrails
```

## 📊 Métricas Esperadas

### KPIs de Roteamento
- **Taxa de acerto:** > 85%
- **Tempo de resposta:** < 2 segundos
- **Fallback rate:** < 15%

### KPIs de Guardrails
- **Taxa de detecção:** > 90%
- **Falsos positivos:** < 5%
- **Confiança média:** > 0.8

## 🔧 Manutenção

### Atualizações Regulares
1. **Keywords:** Revisar mensalmente baseado em conversas reais
2. **Políticas:** Atualizar quando houver mudanças
3. **Produtos:** Adicionar novos produtos à base de conhecimento
4. **Métricas:** Monitorar performance semanalmente

### Expansão
- Adicionar novos agentes conforme necessário
- Expandir base de conhecimento
- Refinar regras de prioridade
- Otimizar prompts baseado no feedback

---

**Este exemplo demonstra como configurar o AtendentePro para um cliente específico, mantendo a flexibilidade e robustez do sistema genérico.**
