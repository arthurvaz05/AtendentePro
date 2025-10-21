from __future__ import annotations

from AtendentePro.Answer.answer_agent import answer_agent
from AtendentePro.Confirmation.confirmation_agent import confirmation_agent
from AtendentePro.Flow.flow_agent import flow_agent
from AtendentePro.Interview.interview_agent import interview_agent
from AtendentePro.Knowledge.knowledge_agent import knowledge_agent
from AtendentePro.Triage.triage_agent import triage_agent
from AtendentePro.Usage.usage_agent import usage_agent

_configured = False


def configure_agent_network(force: bool = False) -> None:
    """Link all agents using the required handoff graph."""
    global _configured
    if _configured and not force:
        return

    triage_agent.handoffs = [
        flow_agent,
        confirmation_agent,
        knowledge_agent,
        usage_agent,
    ]

    flow_agent.handoffs = [
        interview_agent,
        triage_agent,
    ]

    confirmation_agent.handoffs = [triage_agent]
    knowledge_agent.handoffs = [triage_agent]
    usage_agent.handoffs = [triage_agent]

    interview_agent.handoffs = [answer_agent]
    answer_agent.handoffs = [interview_agent]

    _configured = True


configure_agent_network()
