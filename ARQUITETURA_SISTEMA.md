# 🏗️ Arquitetura Atual do Sistema AtendentePro

## 📊 **Diagrama de Fluxo de Agentes**

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUÁRIO                                  │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TRIAGE AGENT                                  │
│  • Entrada principal                                            │
│  • Roteamento inteligente                                       │
│  • Guardrails de escopo                                         │
└─────────────────────┬───────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│FLOW AGENT   │ │KNOWLEDGE    │ │USAGE AGENT  │
│• Identifica │ │AGENT        │ │• Sistema    │
│  tópicos    │ │• RAG        │ │  help      │
│• Apresenta  │ │• Documentos │ │• Meta-info │
│  opções     │ │• Embeddings │ │            │
└─────┬───────┘ └─────┬───────┘ └─────┬───────┘
      │               │               │
      ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│INTERVIEW    │ │CONFIRMATION │ │TRIAGE       │
│AGENT        │ │AGENT        │ │(fallback)   │
│• Coleta     │ │• Validação  │ │            │
│  detalhes   │ │• Confirmação│ │            │
└─────┬───────┘ └─────┬───────┘ └─────────────┘
      │               │
      ▼               ▼
┌─────────────┐ ┌─────────────┐
│ANSWER AGENT │ │TRIAGE       │
│• Resposta   │ │(fallback)   │
│  final      │ │            │
│• Recomendações│            │
└─────────────┘ └─────────────┘
```

## 🔧 **Sistema de Configuração**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONFIGURAÇÃO POR CLIENTE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Template/White_Martins/          Template/standard/            │
│  ├── guardrails_config.yaml      ├── guardrails_config.yaml    │
│  ├── triage_config.yaml          ├── triage_config.yaml        │
│  ├── flow_config.yaml            ├── flow_config.yaml          │
│  ├── interview_config.yaml       ├── interview_config.yaml     │
│  ├── answer_config.yaml          ├── answer_config.yaml        │
│  ├── knowledge_config.yaml       ├── knowledge_config.yaml     │
│  └── guardrail_messages.yaml     └── guardrail_messages.yaml   │
│                                                                 │
│  Ordem de Busca: Cliente → Standard → Root                     │
└─────────────────────────────────────────────────────────────────┘
```

## 🛡️ **Sistema de Guardrails**

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT GUARDRAILS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Usuário → Guardrail → Agente                                  │
│     │         │          │                                      │
│     │         ▼          │                                      │
│     │  Avalia escopo     │                                      │
│     │         │          │                                      │
│     │         ▼          │                                      │
│     │  tripwire_triggered│                                      │
│     │         │          │                                      │
│     │         ▼          │                                      │
│     │  InputGuardrail    │                                      │
│     │  TripwireTriggered │                                      │
│     │         │          │                                      │
│     │         ▼          │                                      │
│     │  Mensagem          │                                      │
│     │  Educativa         │                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🧠 **Sistema RAG (Knowledge Agent)**

```
┌─────────────────────────────────────────────────────────────────┐
│                        PROCESSAMENTO RAG                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PDFs → Extração → Chunking → Embeddings → Busca → Resposta    │
│    │       │         │          │          │         │         │
│    │       ▼         ▼          ▼          ▼         ▼         │
│    │  Texto      Chunks    Vectors    Similarity  Context      │
│    │  Raw       (1000)    (3072)     Score       + Query      │
│    │                        │          │                      │
│    │                        ▼          ▼                      │
│    │                   Cache      Top-K                        │
│    │                   Memory     Results                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## ⚡ **Pontos de Gargalo Identificados**

```
┌─────────────────────────────────────────────────────────────────┐
│                    GARGALOS DE PERFORMANCE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 🔄 Carregamento de Configurações                            │
│     • Múltiplas chamadas I/O por agente                        │
│     • Parsing YAML repetido                                    │
│     • Sem cache de configurações                               │
│                                                                 │
│  2. 💾 Sistema de Embeddings                                   │
│     • Carregamento completo na memória                         │
│     • ~2GB para 1000 chunks                                    │
│     • Sem estratégia de eviction                               │
│                                                                 │
│  3. 🔗 Rede de Agentes Hardcoded                               │
│     • Configuração estática                                    │
│     • Não suporta customização por cliente                     │
│     • Acoplamento forte                                        │
│                                                                 │
│  4. 📊 Falta de Monitoramento                                  │
│     • Sem métricas de performance                              │
│     • Difícil identificar gargalos                             │
│     • Sem alertas de degradação                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 **Arquitetura Proposta (Melhorada)**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONFIG MANAGER                              │
│  • Singleton pattern                                           │
│  • Cache de configurações                                     │
│  • Carregamento único                                          │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    AGENT ORCHESTRATOR                          │
│  • Handoffs dinâmicos                                          │
│  • Configuração por cliente                                    │
│  • Monitoramento de performance                               │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    EMBEDDING CACHE                             │
│  • Cache distribuído                                           │
│  • Estratégia LRU                                             │
│  • Persistência opcional                                       │
└─────────────────────────────────────────────────────────────────┘
```

## 📈 **Métricas de Performance**

| Componente | Tempo Atual | Tempo Otimizado | Melhoria |
|------------|-------------|-----------------|----------|
| Carregamento Config | 0.01s/arquivo | 0.001s/arquivo | 10x |
| Embedding Query | 0.5s | 0.05s (cache) | 10x |
| Busca Semântica | 0.1s | 0.05s | 2x |
| Resposta Agente | 2-5s | 1-3s | 1.5x |
| Memória Total | ~2GB | ~500MB | 4x |

## 🎯 **Recomendações Prioritárias**

### **🔥 Alta Prioridade**
1. **ConfigManager Centralizado** - Reduz I/O em 90%
2. **Cache de Embeddings** - Melhora velocidade em 10x
3. **Sistema de Métricas** - Permite otimização contínua

### **⚡ Média Prioridade**
1. **Handoffs Dinâmicos** - Flexibilidade por cliente
2. **Pool de Conexões** - Escalabilidade
3. **Logging Estruturado** - Debugging eficiente

### **🔮 Baixa Prioridade**
1. **Microserviços** - Arquitetura distribuída
2. **Database Embeddings** - Solução robusta
3. **Fine-tuning** - Qualidade premium
