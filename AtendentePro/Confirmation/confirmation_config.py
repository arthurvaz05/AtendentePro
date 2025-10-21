from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class ConfirmationConfig(BaseModel):
    about: str = Field(description="Texto introdutório que contextualiza a confirmação.")
    format: str = Field(description="Instruções de formatação para a resposta confirmatória.")
    template: str = Field(description="Tabela de referência dos códigos e descrições.")

    @classmethod
    @lru_cache(maxsize=1)
    def load(cls, path: Path | None = None) -> "ConfirmationConfig":
        if path is None:
            path = Path(__file__).resolve().parents[1] / "Template" / "White_Martins" / "confirmation_config.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls(**data)
