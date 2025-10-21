from __future__ import annotations

from enum import Enum
from typing import ClassVar, Dict, List

from pydantic import BaseModel, Field


class AnswerTopic(str, Enum):
    """Lista de tópicos disponíveis para respostas finais. Ajuste conforme o cliente."""
    COMPRA_INDUSTRIALIZACAO = "compra_industrializacao"
    COMPRA_COMERCIALIZACAO = "compra_comercializacao"
    COMPRA_ATIVO_OPERACIONAL = "compra_ativo_operacional"
    COMPRA_ATIVO_PROJETO = "compra_ativo_projeto"
    CONSUMO_ADMINISTRATIVO_ATIVO_NAO_OPERACIONAL = "consumo_administrativo_ativo_nao_operacional"
    AQUISICAO_FRETE = "aquisicao_frete"
    AQUISICAO_ENERGIA_ELETRICA = "aquisicao_energia_eletrica"
    AQUISICAO_SERVICOS_LIGADOS_A_OPERACAO = "aquisicao_servicos_ligados_a_operacao"
    AQUISICAO_SERVICOS_NAO_LIGADOS_A_OPERACAO = "aquisicao_servicos_nao_ligados_a_operacao"


class AnswerOutput(BaseModel):
    """
    Saída estruturada para o agente de resposta.
    """

    topic: AnswerTopic = Field(
        description="Tópico identificado para a resposta final. Use um dos valores de AnswerTopic."
    )
    code: str = Field(
        description=(
            "Código IVA selecionado dentro do tópico escolhido. "
            "Consulte `AnswerOutput.ALLOWED_CODES_BY_TOPIC` para validar."
        )
    )

    ALLOWED_CODES_BY_TOPIC: ClassVar[Dict[AnswerTopic, List[str]]] = {}

    @classmethod
    def set_allowed_codes(cls, mapping: Dict[AnswerTopic, List[str]]) -> None:
        cls.ALLOWED_CODES_BY_TOPIC = mapping
