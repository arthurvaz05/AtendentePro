from __future__ import annotations

from agents import Agent

from AtendentePro import config
from AtendentePro.context import ContextNote
from AtendentePro.Triage.triage_models import triage_keywords_text

triage_agent = Agent[ContextNote](
    name="Triage Agent",
    handoff_description="A triage agent that can delegate a customer's request to the appropriate agent.",
    instructions=(
        f"{config.RECOMMENDED_PROMPT_PREFIX} "
        "Você é um agente de triagem prestativo. Analise a mensagem do usuário e direcione-a para o agente mais adequado. "
        "Considere os seguintes grupos de palavras-chave como sinais do agente ideal:\n"
        f"{triage_keywords_text}"
    ),
    handoffs=[],
)
