from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel, Field

from AtendentePro.Template.White_Martins.answer_config import AnswerTopic


class FlowTopicConfig(BaseModel):
    id: AnswerTopic = Field(description="Identificador do tópico (AnswerTopic).")
    label: str = Field(description="Descrição apresentada ao agente/usuário.")


class FlowKeywordConfig(BaseModel):
    terms: List[str] = Field(description="Lista de termos que indicam o tópico.")
    topic: AnswerTopic = Field(description="Tópico associado aos termos.")


class FlowConfig(BaseModel):
    topics: List[FlowTopicConfig] = Field(description="Lista de tópicos disponíveis para roteamento.")
    keywords: List[FlowKeywordConfig] = Field(description="Sugestões de palavras-chave para inferir o tópico.")

    @classmethod
    @lru_cache(maxsize=1)
    def load(cls, path: Path | None = None) -> "FlowConfig":
        if path is None:
            path = Path(__file__).resolve().parents[1] / "Template" / "White_Martins" / "flow_config.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        raw_topics = data.get("topics", [])
        raw_keywords = data.get("keywords", [])
        topics = [FlowTopicConfig(id=AnswerTopic(item["id"]), label=item["label"]) for item in raw_topics]
        keywords = [
            FlowKeywordConfig(terms=item["terms"], topic=AnswerTopic(item["topic"])) for item in raw_keywords
        ]
        return cls(topics=topics, keywords=keywords)
