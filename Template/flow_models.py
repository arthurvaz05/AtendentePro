from __future__ import annotations

from pydantic import BaseModel, Field

from AtendentePro.Answer.answer_models import AnswerTopic


class FlowOutput(BaseModel):
    """
    Resultado padronizado do agente de fluxo.

    selected_topic:
        Tópico escolhido para continuar o atendimento.
    user_answer:
        Resposta literal do usuário que indica o tópico desejado.
    reasoning:
        Resumo curto explicando o motivo da escolha.
    """

    selected_topic: AnswerTopic = Field(
        description="Tópico selecionado para a próxima etapa do fluxo."
    )
    user_answer: str = Field(
        description="Resposta do usuário ao ser perguntado sobre o tópico adequado."
    )
    reasoning: str = Field(
        description="Resumo do raciocínio que levou à seleção do tópico."
    )
