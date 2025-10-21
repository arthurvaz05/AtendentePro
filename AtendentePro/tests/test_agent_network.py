"""Testes para a rede de agentes."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project and package roots are on sys.path for absolute imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

PACKAGE_ROOT = PROJECT_ROOT / "AtendentePro"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.append(str(PACKAGE_ROOT))

from AtendentePro.agent_network import configure_agent_network  # noqa: E402
from AtendentePro.Answer.answer_agent import answer_agent  # noqa: E402
from AtendentePro.Confirmation.confirmation_agent import confirmation_agent  # noqa: E402
from AtendentePro.Flow.flow_agent import flow_agent  # noqa: E402
from AtendentePro.Interview.interview_agent import interview_agent  # noqa: E402
from AtendentePro.Knowledge.knowledge_agent import knowledge_agent  # noqa: E402
from AtendentePro.Triage.triage_agent import triage_agent  # noqa: E402
from AtendentePro.Usage.usage_agent import usage_agent  # noqa: E402


def test_configure_agent_network():
    """Testa se a configuração da rede de agentes funciona."""
    # Força reconfiguração
    configure_agent_network(force=True)
    
    # Verifica se todos os agentes têm handoffs configurados
    assert len(triage_agent.handoffs) > 0
    assert len(flow_agent.handoffs) > 0
    assert len(confirmation_agent.handoffs) > 0
    assert len(knowledge_agent.handoffs) > 0
    assert len(usage_agent.handoffs) > 0
    assert len(interview_agent.handoffs) > 0
    assert len(answer_agent.handoffs) > 0


def test_triage_agent_handoffs():
    """Testa os handoffs do agente de triagem."""
    configure_agent_network(force=True)
    
    # Triage deve ter acesso a todos os outros agentes
    expected_handoffs = [flow_agent, confirmation_agent, knowledge_agent, usage_agent]
    actual_handoffs = triage_agent.handoffs
    assert len(actual_handoffs) == len(expected_handoffs)
    for agent in expected_handoffs:
        assert agent in actual_handoffs


def test_flow_agent_handoffs():
    """Testa os handoffs do agente de fluxo."""
    configure_agent_network(force=True)
    
    # Flow deve ter acesso ao interview e fallback para triage
    expected_handoffs = [interview_agent, triage_agent]
    actual_handoffs = flow_agent.handoffs
    assert len(actual_handoffs) == len(expected_handoffs)
    for agent in expected_handoffs:
        assert agent in actual_handoffs


def test_interview_agent_handoffs():
    """Testa os handoffs do agente de entrevista."""
    configure_agent_network(force=True)
    
    # Interview deve ter acesso ao answer
    assert interview_agent.handoffs == [answer_agent]


def test_answer_agent_handoffs():
    """Testa os handoffs do agente de resposta."""
    configure_agent_network(force=True)
    
    # Answer deve ter fallback para interview
    assert answer_agent.handoffs == [interview_agent]


def test_specialized_agents_handoffs():
    """Testa os handoffs dos agentes especializados."""
    configure_agent_network(force=True)
    
    # Agentes especializados devem ter fallback para triage
    assert confirmation_agent.handoffs == [triage_agent]
    assert knowledge_agent.handoffs == [triage_agent]
    assert usage_agent.handoffs == [triage_agent]


def test_agent_network_consistency():
    """Testa a consistência da rede de agentes."""
    configure_agent_network(force=True)
    
    # Verifica se não há referências circulares problemáticas
    all_agents = [
        triage_agent, flow_agent, interview_agent, answer_agent,
        confirmation_agent, knowledge_agent, usage_agent
    ]
    
    # Cada agente deve ter pelo menos um handoff
    for agent in all_agents:
        assert len(agent.handoffs) > 0, f"Agent {agent.name} has no handoffs"
        
        # Cada handoff deve ser um agente válido
        for handoff in agent.handoffs:
            assert handoff in all_agents, f"Invalid handoff in {agent.name}"


def test_configure_agent_network_idempotent():
    """Testa se a configuração é idempotente."""
    # Configura uma vez
    configure_agent_network(force=True)
    first_handoffs = {agent.name: agent.handoffs for agent in [
        triage_agent, flow_agent, interview_agent, answer_agent,
        confirmation_agent, knowledge_agent, usage_agent
    ]}
    
    # Configura novamente
    configure_agent_network(force=True)
    second_handoffs = {agent.name: agent.handoffs for agent in [
        triage_agent, flow_agent, interview_agent, answer_agent,
        confirmation_agent, knowledge_agent, usage_agent
    ]}
    
    # Deve ser igual
    assert first_handoffs == second_handoffs
