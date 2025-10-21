from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field

from AtendentePro.Template.White_Martins.answer_config import AnswerTopic


class InterviewOutput(BaseModel):
    """
    Estrutura de saída padronizada para a entrevista.
    
    IMPORTANTE: Este output deve ser preenchido APENAS após coletar todas as respostas
    necessárias do usuário durante a entrevista. NÃO preencha com dados fictícios.

    topic:
        Indica qual rota/tópico foi identificado a partir das respostas.
    answers:
        Mapa pergunta -> resposta escolhida pelo usuário (usar IDs definidos no YAML).
    """

    topic: AnswerTopic = Field(
        description="Tópico final identificado pelas respostas da entrevista. Deve ser preenchido apenas após a entrevista completa."
    )
    answers: Dict[str, str] = Field(
        default_factory=dict,
        description="Respostas reais do usuário, indexadas pelo ID da pergunta (ex.: '1.1', '6.2'). NÃO invente respostas.",
    )
