from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class KnowledgeConfig(BaseModel):
    about: str = Field(description="Texto listando os documentos de referência.")
    format: str = Field(description="Instruções de formatação para a resposta.")
    template: str = Field(description="Resumo estruturado dos documentos disponíveis.")

    @classmethod
    @lru_cache(maxsize=1)
    def load(cls, path: Path | None = None) -> "KnowledgeConfig":
        if path is None:
            path = Path(__file__).resolve().parents[1] / "Template" / "White_Martins" / "knowledge_config.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls(**data)
