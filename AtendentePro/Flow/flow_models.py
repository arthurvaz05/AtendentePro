from __future__ import annotations

from pydantic import BaseModel, Field

from AtendentePro.Template.White_Martins.answer_config import AnswerTopic
from AtendentePro.Flow.flow_config import FlowConfig


class FlowOutput(BaseModel):
    """Resultado padronizado do agente de fluxo."""

    selected_topic: AnswerTopic = Field(
        description="Pergunta feita ao usuário para obter informações relevantes."
    )
    user_answer: str = Field(
        description="Resposta literal do usuário ao ser perguntado sobre o tópico adequado."
    )
    reasoning: str = Field(
        description="Resumo curto explicando o motivo da escolha."
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {"additionalProperties": False},
    }


# Configuração e templates do Flow
_config = FlowConfig.load()

flow_topics = _config.topics
_topic_label_by_id = {topic.id: topic.label for topic in flow_topics}

flow_template = "\n".join(
    f"{index}. {topic.label}" for index, topic in enumerate(flow_topics, start=1)
)

flow_keywords_by_topic = {
    _topic_label_by_id.get(topic.id, topic.id.value): [
        term
        for mapping in _config.keywords
        if mapping.topic == topic.id
        for term in mapping.terms
    ]
    for topic in flow_topics
}


def _format_terms(terms: list[str]) -> str:
    return ", ".join(f'"{term}"' for term in terms)


flow_keywords = "\n".join(
    f"- {label}: {_format_terms(terms)}"
    for label, terms in flow_keywords_by_topic.items()
    if terms
)
