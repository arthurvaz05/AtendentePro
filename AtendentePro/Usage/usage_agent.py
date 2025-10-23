from __future__ import annotations

from agents import Agent

from AtendentePro import config
from AtendentePro.context import ContextNote
from AtendentePro.guardrails import get_guardrails_for_agent

usage_agent = Agent[ContextNote](
    name="Usage Agent",
    handoff_description="A usage agent that can answer questions about the usage of the system.",
    instructions="You are a helpful usage agent. You will answer questions about the usage of the system.",
    handoffs=[],
    input_guardrails=get_guardrails_for_agent("usage_agent"),
)
