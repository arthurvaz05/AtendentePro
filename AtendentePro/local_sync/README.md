# Local Sync - Sincronização com Serviço

Esta pasta mantém uma cópia local do projeto AtendentePro sincronizada com o serviço em produção.

## 🎯 Objetivo

Permitir desenvolvimento local com acesso à versão mais recente do serviço, mantendo configurações locais específicas.

## 📂 Estrutura

```
local_sync/
├── README.md                    # Este arquivo
├── ai_prompts.md               # Prompts para Copilot
├── sync_config.yaml            # Configurações de sincronização
├── local_config.yaml           # Configurações específicas locais
├── .env.local                  # Variáveis de ambiente locais
├── backup/                     # Backup da versão anterior
└── temp/                       # Arquivos temporários
```

## 🚀 Como Usar

### Sincronizar do Serviço para Local
Use o **Prompt 1** do arquivo `ai_prompts.md` com o Copilot para sincronizar do serviço para o local.

### Sincronizar do Local para Serviço
Use o **Prompt 2** do arquivo `ai_prompts.md` com o Copilot para sincronizar do local para o serviço.

## ⚙️ Configuração

1. Configure `sync_config.yaml` com URL do serviço e token
2. Defina variáveis de ambiente locais em `.env.local`
3. Personalize `local_config.yaml` conforme necessário

## 🔒 Segurança

- Arquivos sensíveis são preservados localmente
- Validações são executadas antes do envio
- Backup automático da versão anterior
- Logs detalhados de todas as operações

## 📋 Preservação de Arquivos

Os seguintes arquivos são sempre preservados durante sincronização:
- `.env.local`
- `local_config.yaml`
- `sync_logs/`
- `temp/`
- `backup/`

## 🔄 Fluxo de Sincronização

### Serviço → Local
1. Conecta ao serviço em produção
2. Compara arquivos com versão local
3. Baixa apenas arquivos modificados
4. Preserva configurações locais
5. Gera relatório de sincronização

### Local → Serviço
1. Identifica mudanças locais
2. Valida arquivos antes do envio
3. Envia mudanças para o serviço
4. Confirma aplicação no serviço
5. Atualiza logs locais

## 📊 Monitoramento

- Backup automático em `backup/`
- Relatórios de sincronização via Copilot
- Alertas de conflitos via Copilot

## 🛠️ Desenvolvimento

Esta estrutura permite:
- Desenvolvimento offline eficiente
- Sincronização bidirecional segura
- Preservação de configurações locais
- Validação antes do deploy
- Backup automático de versões
