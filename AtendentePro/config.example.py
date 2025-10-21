# Configurações do Sistema de Agentes - EXEMPLO
# Copie este arquivo para config.py e configure suas variáveis

import os

# OpenAI API Key (obrigatório para funcionamento dos agentes)
# Configure a variável de ambiente OPENAI_API_KEY ou edite aqui
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'sua-chave-aqui')

# Configurar variável de ambiente se não estiver definida
if not os.getenv('OPENAI_API_KEY'):
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

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
