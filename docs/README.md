# 📚 Índice da Documentação - AtendentePro

## 🎯 Guias Principais

### [🚀 Setup Guide](SETUP.md)
**Guia completo de configuração para novos clientes**
- Visão geral da arquitetura
- Passo a passo para configuração
- Exemplos práticos
- Troubleshooting

### [🏗️ Architecture](ARCHITECTURE.md)
**Arquitetura e princípios do sistema**
- Visão geral arquitetural
- Componentes principais
- Padrões de design
- Fluxos de funcionamento
- Escalabilidade e manutenibilidade

## 🔧 Documentação por Módulo

### [🎯 Triage Module](modules/triage.md)
**Sistema de roteamento inteligente**
- Arquitetura do módulo
- Componentes principais
- Configuração de keywords
- Exemplos de uso
- Debugging e troubleshooting

### [🛡️ Guardrails Module](modules/guardrails.md)
**Proteção de escopo e rollback**
- Sistema de avaliação de mensagens
- Configuração de escopos
- Rollback educado
- Integração com outros módulos
- Métricas e monitoramento

### [📚 Knowledge Module](modules/knowledge.md)
**Base de conhecimento e RAG**
- Sistema RAG avançado
- Processamento de documentos
- Busca semântica
- Configuração de embeddings
- Exemplos práticos

## 📝 Exemplos Práticos

### [🛒 TechStore Configuration](examples/techstore_config.md)
**Exemplo completo de configuração para e-commerce**
- Perfil do cliente fictício
- Configurações completas
- Testes de validação
- Métricas esperadas
- Guia de manutenção

## 🚀 Quick Start

### Para Desenvolvedores
1. Leia [Architecture](ARCHITECTURE.md) para entender o sistema
2. Consulte [Triage Module](modules/triage.md) para roteamento
3. Veja [Guardrails Module](modules/guardrails.md) para proteção
4. Explore [Knowledge Module](modules/knowledge.md) para RAG

### Para Novos Clientes
1. Comece com [Setup Guide](SETUP.md)
2. Use [TechStore Configuration](examples/techstore_config.md) como referência
3. Configure guardrails e triage específicos
4. Teste com mensagens reais

### Para Manutenção
1. Monitore métricas de cada módulo
2. Ajuste configurações baseado no feedback
3. Expanda base de conhecimento conforme necessário
4. Otimize prompts e keywords

## 📊 Estrutura da Documentação

```
docs/
├── SETUP.md                    # Guia principal de configuração
├── ARCHITECTURE.md             # Arquitetura do sistema
├── modules/
│   ├── triage.md              # Documentação do módulo Triage
│   ├── guardrails.md          # Documentação do módulo Guardrails
│   └── knowledge.md           # Documentação do módulo Knowledge
└── examples/
    └── techstore_config.md    # Exemplo prático completo
```

## 🔗 Links Úteis

- **Repositório:** [GitHub](https://github.com/arthurvaz05/AtendentePro)
- **OpenAI Agents SDK:** [Documentação Oficial](https://platform.openai.com/docs/assistants/overview)
- **Python 3.13+:** [Documentação](https://docs.python.org/3/)

## 📞 Suporte

Para dúvidas sobre a documentação:
1. Verifique se a pergunta está coberta na documentação
2. Consulte os exemplos práticos
3. Teste com configurações da White Martins como referência
4. Abra uma issue no repositório para dúvidas específicas

---

**Última atualização:** Outubro 2024  
**Versão:** 1.0.0
