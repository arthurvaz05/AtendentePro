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
    Um agente de fluxo que faz uma pergunta ao usuário para obter informações relevantes e transferir a conversa indicando qual tópico deve ser entrevistado.
    Só deve trasnferir para o triage se a resposta do usuário não for clara o suficiente para determinar o tópico deve ser entrevistado.
    Caso tenha uma rota clara, deve transferir para o agente de entrevista com o tópico escolhido.
    """,
    instructions=(
        f"{config.RECOMMENDED_PROMPT_PREFIX} "
        f"{flow_prompts_agent}"
    ),
    handoffs=[],
    # output_type=FlowOutput,
)
