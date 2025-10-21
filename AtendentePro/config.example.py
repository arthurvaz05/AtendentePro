# Configurações do Sistema de Agentes - EXEMPLO
# Copie este arquivo para config.py e configure suas variáveis

import os

# Credenciais do Azure OpenAI (configure-as ou exporte-as antes de executar)
AZURE_API_KEY = os.getenv("AZURE_API_KEY", "sua-chave-azure-aqui")
AZURE_API_ENDPOINT = os.getenv("AZURE_API_ENDPOINT", "https://seu-endpoint.openai.azure.com/")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2024-02-15-preview")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o-mini")

# Credenciais do OpenAI padrão (opcional caso prefira usar a API pública)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# Telemetria opcional com Azure Application Insights
APPLICATION_INSIGHTS_CONNECTION_STRING = os.getenv(
    "APPLICATION_INSIGHTS_CONNECTION_STRING",
    "InstrumentationKey=00000000-0000-0000-0000-000000000000;IngestionEndpoint=https://region-0.in.applicationinsights.azure.com/",
)

# Opcionalmente popular as variáveis de ambiente se não estiverem definidas
os.environ.setdefault("AZURE_API_KEY", AZURE_API_KEY)
os.environ.setdefault("AZURE_API_ENDPOINT", AZURE_API_ENDPOINT)
os.environ.setdefault("AZURE_API_VERSION", AZURE_API_VERSION)
os.environ.setdefault("AZURE_DEPLOYMENT_NAME", AZURE_DEPLOYMENT_NAME)
os.environ.setdefault("OPENAI_API_KEY", OPENAI_API_KEY)
os.environ.setdefault(
    "APPLICATION_INSIGHTS_CONNECTION_STRING", APPLICATION_INSIGHTS_CONNECTION_STRING
)

# Provider selecionado: "azure" ou "openai"
OPENAI_PROVIDER = os.getenv("OPENAI_PROVIDER")
if not OPENAI_PROVIDER:
    OPENAI_PROVIDER = "azure" if AZURE_API_KEY and AZURE_API_ENDPOINT else "openai"
    os.environ.setdefault("OPENAI_PROVIDER", OPENAI_PROVIDER)

# Diretório para salvar contextos
CONTEXT_OUTPUT_DIR = "context"

# Modelo padrão utilizado pelos agentes Swarm
DEFAULT_MODEL = "gpt-4.1"

RECOMMENDED_PROMPT_PREFIX = """
[CONTEXT SYSTEM]
- Você faz parte de um sistema multiagente chamado Agents SDK, criado para facilitar a coordenação e execução de agentes.
- O Agents SDK utiliza duas principais abstrações: **Agentes** e **Handoffs** (transferências).
- Um agente abrange instruções e ferramentas e pode transferir uma conversa para outro agente quando apropriado.
- Transferências entre agentes são realizadas chamando uma função de transferência, geralmente nomeada como `transfer_to_<nome_do_agente>`.
- As transferências entre agentes ocorrem de forma transparente em segundo plano; não mencione nem chame atenção para essas transferências na sua conversa com o usuário.
"""
