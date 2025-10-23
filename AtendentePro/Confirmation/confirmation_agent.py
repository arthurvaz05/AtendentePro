from __future__ import annotations

from agents import Agent

from AtendentePro import config
from AtendentePro.Confirmation.confirmation_prompts import prompts_confirmation_agent
from AtendentePro.context import ContextNote
from AtendentePro.guardrails import get_guardrails_for_agent


confirmation_agent = Agent[ContextNote](
    name="Confirmation Agent",
    handoff_description="Um agente de confirmação que pode confirmar a solicitação do usuário.",
    instructions=(
        f"{config.RECOMMENDED_PROMPT_PREFIX} "
        f"{prompts_confirmation_agent}"
    ),
    handoffs=[],
    input_guardrails=get_guardrails_for_agent("confirmation_agent"),
)
