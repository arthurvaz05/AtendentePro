from __future__ import annotations

from agents import Agent, AgentOutputSchema

from AtendentePro import config
from AtendentePro.Answer.answer_prompts import answer_prompts_agent
from AtendentePro.Template.White_Martins.answer_config import AnswerOutput
from AtendentePro.context import ContextNote

answer_agent = Agent[ContextNote](
    name="Answer Agent",
    handoff_description=f"""
    Você é um agente para formular uma resposta para o usuário com as informações no output_type..
    """,
    instructions=f"{config.RECOMMENDED_PROMPT_PREFIX} {answer_prompts_agent}",
    handoffs=[],
    #output_type=AgentOutputSchema(AnswerOutput, strict_json_schema=False),
)


answer_agent2 = Agent[AnswerOutput](
    name="Answer Agent 2",
    handoff_description=f"""
    Um agente de resposta que pode responder a pergunta do usuário.
    """,
    instructions="Você é um agente para formular uma resposta para o usuário com as informações no output_type.",
    handoffs=[]
)