from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class InterviewConfig(BaseModel):
    """Representa a configuração completa carregada do arquivo YAML."""

    interview_questions: str = Field(description="Texto com o roteiro de perguntas da entrevista.")

    @classmethod
    @lru_cache(maxsize=1)
    def load(cls, path: Path | None = None) -> "InterviewConfig":
        """Carrega a configuração a partir do arquivo YAML."""
        if path is None:
            path = Path(__file__).resolve().parents[1] / "Template" / "White_Martins" / "interview_config.yaml"

        data = yaml.safe_load(path.read_text(encoding="utf-8"))

        config = cls(
            interview_questions=data.get("interview_questions", ""),
        )
        return config
