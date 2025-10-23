from __future__ import annotations

from agents import Agent, AgentOutputSchema

from AtendentePro import config
from AtendentePro.Interview.interview_prompts import interview_prompts_agent, interview_template
from AtendentePro.Interview.interview_models import InterviewOutput
from AtendentePro.context import ContextNote

interview_agent = Agent[ContextNote](
    name="Interview Agent",
    handoff_description=f"""
    Um agente de entrevista que pode entrevistar o usuário para obter informações relevantes.
    """,
    instructions=(
        f"{config.RECOMMENDED_PROMPT_PREFIX} "
        f"{interview_prompts_agent}"
    ),
    handoffs=[],
    # output_type=AgentOutputSchema(InterviewOutput, strict_json_schema=False),
)
