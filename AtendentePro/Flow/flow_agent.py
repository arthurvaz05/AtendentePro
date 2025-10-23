from __future__ import annotations

from agents import Agent

from AtendentePro import config
from AtendentePro.Flow.flow_prompts import flow_prompts_agent
from AtendentePro.Interview.interview_prompts import interview_template
from AtendentePro.Flow.flow_models import FlowOutput
from AtendentePro.context import ContextNote

flow_agent = Agent[ContextNote](
    name="Flow Agent",
    handoff_description=f"""
    Um agente de fluxo inteligente que:
    1. Se o usuário já especificou um tópico específico, vai direto para o interview_agent
    2. Se não especificou, apresenta a lista de tópicos para o usuário escolher
    3. Só transfere para triage se a resposta não for clara o suficiente
    """,
    instructions=(
        f"{config.RECOMMENDED_PROMPT_PREFIX} "
        f"{flow_prompts_agent}"
    ),
    handoffs=[],  # Será configurado pelo agent_network.py
    # output_type=FlowOutput,
)
