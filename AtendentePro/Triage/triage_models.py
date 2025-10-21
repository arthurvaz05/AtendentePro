from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import yaml
from pydantic import BaseModel, Field


class AgentKeywords(BaseModel):
    keywords: List[str] = Field(description="Lista de palavras-chave que indicam este agente.")


class TriageKeywordsConfig(BaseModel):
    keywords: Dict[str, AgentKeywords] = Field(
        description="Mapeamento de agente -> palavras-chave relevantes."
    )

    @classmethod
    @lru_cache(maxsize=1)
    def load(cls, path: Path | None = None) -> "TriageKeywordsConfig":
        if path is None:
            path = Path(__file__).resolve().parents[1] / "Template" / "White_Martins" / "triage_config.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        parsed = {
            agent: AgentKeywords(**info if isinstance(info, dict) else {"keywords": info})
            for agent, info in data.get("keywords", {}).items()
        }
        return cls(keywords=parsed)


_config = TriageKeywordsConfig.load()
triage_keywords_map: Dict[str, List[str]] = {
    agent: entry.keywords for agent, entry in _config.keywords.items()
}


def format_triage_keywords(prefix: str = "-") -> str:
    lines: list[str] = []
    for agent, terms in triage_keywords_map.items():
        highlighted_terms = ", ".join(f'"{term}"' for term in terms)
        lines.append(f"{prefix} {agent.title()}: {highlighted_terms}")
    return "\n".join(lines)


triage_keywords_text = format_triage_keywords()

__all__ = [
    "triage_keywords_map",
    "triage_keywords_text",
    "format_triage_keywords",
    "TriageKeywordsConfig",
]
