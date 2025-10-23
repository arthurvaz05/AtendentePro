# 📋 Template Standard - Configurações Padrão

Esta pasta contém as configurações padrão genéricas do sistema AtendentePro. Esses arquivos servem como templates base para novos clientes e como fallback quando não há configurações específicas.

## 📁 Arquivos Incluídos

### Configurações Principais
- **`triage_config.yaml`** - Configuração genérica do sistema de triage

### Configurações por Agente
- **`answer_config.yaml`** - Configuração padrão do Answer Agent
- **`confirmation_config.yaml`** - Configuração padrão do Confirmation Agent
- **`flow_config.yaml`** - Configuração padrão do Flow Agent
- **`interview_config.yaml`** - Configuração padrão do Interview Agent
- **`knowledge_config.yaml`** - Configuração padrão do Knowledge Agent

## 🎯 Propósito

### Para Novos Clientes
1. **Template Base**: Use estes arquivos como ponto de partida
2. **Customização**: Adapte as configurações para seu domínio específico
3. **Referência**: Consulte para entender a estrutura esperada

### Para o Sistema
1. **Fallback**: Usado quando não há configuração específica do cliente
2. **Consistência**: Garante que o sistema sempre tenha configurações válidas
3. **Manutenção**: Facilita atualizações genéricas

## 🔄 Ordem de Busca

O sistema busca configurações na seguinte ordem:

1. **`Template/[CLIENTE]/`** - Configurações específicas do cliente
2. **`Template/standard/`** - Configurações padrão (esta pasta)
3. **Raiz do projeto** - Fallback final

## 📝 Como Usar

### Para Criar Novo Cliente

1. **Copie os arquivos padrão:**
```bash
cp -r AtendentePro/Template/standard AtendentePro/Template/[NOME_CLIENTE]
```

2. **Customize as configurações:**
   - Ajuste `triage_config.yaml` com keywords relevantes
   - Personalize configurações de agentes conforme necessário

3. **Teste a configuração:**
```bash
echo "pergunta teste" | python -m AtendentePro.run_env.run triage
```

### Para Manutenção

- **Atualizações genéricas**: Modifique arquivos nesta pasta
- **Novos agentes**: Adicione configurações padrão aqui
- **Melhorias**: Refine templates baseados no feedback

## ⚠️ Importante

- **Não modifique** arquivos desta pasta para clientes específicos
- **Use como referência** para criar configurações personalizadas
- **Mantenha genérico** - evite informações específicas de clientes
- **Teste mudanças** antes de aplicar em produção

## 🔗 Links Úteis

- [Guia de Configuração](../../docs/SETUP.md)
- [Exemplo Prático](../../docs/examples/techstore_config.md)
- [Documentação por Módulo](../../docs/modules/)

---

**Última atualização:** Outubro 2024  
**Versão:** 1.0.0
