# Configurações do Sistema de Agentes
import os
from typing import Literal

# Ajuste de estado do provedor
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_API_ENDPOINT = os.getenv("AZURE_API_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION") or os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")

# Configuração para processo de documentos
OCR_ENABLED = "true"
AZURE_AI_VISION_ENDPOINT = os.getenv("AZURE_AI_VISION_ENDPOINT")
AZURE_AI_VISION_KEY = os.getenv("AZURE_AI_VISION_KEY")

APPLICATION_INSIGHTS_CONNECTION_STRING = os.getenv("APPLICATION_INSIGHTS_CONNECTION_STRING")

_provider_env = (os.getenv("OPENAI_PROVIDER") or "").strip().lower()

if _provider_env:
    OPENAI_PROVIDER: Literal["openai", "azure"] = (
        "azure" if _provider_env == "azure" else "openai"
    )
else:
    OPENAI_PROVIDER = "azure" if AZURE_API_KEY and AZURE_API_ENDPOINT else "openai"


# Diretório para salvar contextos
CONTEXT_OUTPUT_DIR = "context"

# Modelo padrão utilizado pelos agentes Swarm
DEFAULT_MODEL = "gpt-4.1"


RECOMMENDED_PROMPT_PREFIX = """"
[CONTEXT SYSTEM]
- Você faz parte de um sistema multiagente chamado Agents SDK, criado para facilitar a coordenação e execução de agentes.
- O Agents SDK utiliza duas principais abstrações: **Agentes** e **Handoffs** (transferências).
- Um agente abrange instruções e ferramentas e pode transferir uma conversa para outro agente quando apropriado.
- Transferências entre agentes são realizadas chamando uma função de transferência, geralmente nomeada como `transfer_to_<nome_do_agente>`.
- As transferências entre agentes ocorrem de forma transparente em segundo plano; não mencione nem chame atenção para essas transferências na sua conversa com o usuário.\n"""
