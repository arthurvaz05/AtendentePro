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

import config  # noqa: E402
from AtendentePro.Answer.answer_agent import answer_agent  # noqa: E402
from AtendentePro.Answer.answer_prompts import answer_prompts_agent  # noqa: E402
from AtendentePro.Confirmation.confirmation_agent import confirmation_agent  # noqa: E402
from AtendentePro.Confirmation.confirmation_prompts import prompts_confirmation_agent  # noqa: E402
from AtendentePro.Flow.flow_agent import flow_agent  # noqa: E402
from AtendentePro.Flow.flow_prompts import flow_prompts_agent  # noqa: E402
from AtendentePro.Interview.interview_agent import interview_agent  # noqa: E402
from AtendentePro.Interview.interview_prompts import interview_prompts_agent  # noqa: E402
from AtendentePro.Interview.interview_models import InterviewOutput  # noqa: E402
from AtendentePro.Knowledge.knowledge_agent import knowledge_agent  # noqa: E402
from AtendentePro.Template.White_Martins.answer_config import AnswerOutput  # noqa: E402
from AtendentePro.Flow.flow_models import FlowOutput  # noqa: E402
from AtendentePro.Triage.triage_agent import triage_agent  # noqa: E402
from AtendentePro.Usage.usage_agent import usage_agent  # noqa: E402
from AtendentePro.agent_network import configure_agent_network  # noqa: E402

configure_agent_network()


def test_flow_agent_configuration():
    assert flow_agent.name == "Flow Agent"
    assert flow_agent.output_type in (FlowOutput, None)
    assert flow_agent.handoffs == [interview_agent, triage_agent]
    instructions = flow_agent.instructions
    assert isinstance(instructions, str)
    assert config.RECOMMENDED_PROMPT_PREFIX.strip() in instructions
    assert flow_prompts_agent.strip() in instructions


def test_answer_agent_configuration():
    assert answer_agent.name == "Answer Agent"
    # O output_type é um AgentOutputSchema, não AnswerOutput diretamente
    assert answer_agent.output_type is not None
    assert hasattr(answer_agent.output_type, 'output_type')
    assert answer_agent.handoffs == [interview_agent]
    instructions = answer_agent.instructions
    assert isinstance(instructions, str)
    assert config.RECOMMENDED_PROMPT_PREFIX.strip() in instructions
    assert answer_prompts_agent.strip() in instructions


def test_confirmation_agent_configuration():
    assert confirmation_agent.name == "Confirmation Agent"
    assert confirmation_agent.handoffs == [triage_agent]
    instructions = confirmation_agent.instructions
    assert isinstance(instructions, str)
    assert config.RECOMMENDED_PROMPT_PREFIX.strip() in instructions
    assert prompts_confirmation_agent.strip() in instructions


def test_triage_agent_configuration():
    assert triage_agent.name == "Triage Agent"
    assert triage_agent.handoffs == [
        flow_agent,
        confirmation_agent,
        knowledge_agent,
        usage_agent,
    ]
    instructions = triage_agent.instructions
    assert isinstance(instructions, str)
    assert "agente de triagem" in instructions.lower()
    assert triage_agent.output_type is None


def test_interview_agent_configuration():
    assert interview_agent.name == "Interview Agent"
    # O output_type está comentado no interview_agent, então é None
    assert interview_agent.output_type is None
    assert interview_agent.handoffs == [answer_agent]


def test_interview_agent_instructions_content():
    instructions = interview_agent.instructions
    assert isinstance(instructions, str)
    assert config.RECOMMENDED_PROMPT_PREFIX.strip() in instructions
    assert interview_prompts_agent.strip() in instructions


def test_knowledge_agent_configuration():
    assert knowledge_agent.name == "Knowledge Agent"
    assert knowledge_agent.handoffs == [triage_agent]


def test_usage_agent_configuration():
    assert usage_agent.name == "Usage Agent"
    assert usage_agent.handoffs == [triage_agent]
