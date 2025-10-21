from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict

import yaml
from pydantic import BaseModel, Field

from AtendentePro.Template.White_Martins.answer_config import AnswerOutput, AnswerTopic


class TopicConfig(BaseModel):
    """Configuração individual de um tópico de resposta."""

    description: str = Field(description="Descrição humana do tópico.")
    codes: list[str] = Field(description="Lista de códigos permitidos para o tópico.")


class AnswerConfig(BaseModel):
    """Representa a configuração completa carregada do arquivo YAML."""

    topics: Dict[AnswerTopic, TopicConfig] = Field(
        description="Tópicos disponíveis e seus códigos permitidos."
    )
    answer_template: str = Field(description="Texto utilizado pelo agente de resposta.")

    @property
    def allowed_codes_by_topic(self) -> Dict[AnswerTopic, list[str]]:
        return {topic: config.codes for topic, config in self.topics.items()}

    @classmethod
    @lru_cache(maxsize=1)
    def load(cls, path: Path | None = None) -> "AnswerConfig":
        """Carrega a configuração a partir do arquivo YAML."""
        if path is None:
            path = Path(__file__).resolve().parents[1] / "Template" / "White_Martins" / "answer_config.yaml"

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        raw_topics = data.get("topics", {})

        topics: Dict[AnswerTopic, TopicConfig] = {}
        for key, value in raw_topics.items():
            topic = AnswerTopic(key)
            topics[topic] = TopicConfig(**value)

        config = cls(
            topics=topics,
            answer_template=data.get("answer_template", ""),
        )
        AnswerOutput.set_allowed_codes(config.allowed_codes_by_topic)
        return config
