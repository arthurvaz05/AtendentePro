from __future__ import annotations

from agents import Agent

from AtendentePro import config
from AtendentePro.context import ContextNote
from AtendentePro.guardrails import get_guardrails_for_agent
from AtendentePro.Triage.triage_prompt import triage_prompts_agent

triage_agent = Agent[ContextNote](
    name="Triage Agent",
    handoff_description="A triage agent that can delegate a customer's request to the appropriate agent.",
    instructions=(
        f"{config.RECOMMENDED_PROMPT_PREFIX} "
        f"{triage_prompts_agent}"
    ),
    handoffs=[],
    input_guardrails=get_guardrails_for_agent("triage_agent"),
)
