
### CONTEXT

from __future__ import annotations

from pydantic import BaseModel, Field


class ContextNote(BaseModel):
    handoff_summaries: dict[str, dict] = Field(
        default_factory=dict,
        description="Resumos estruturados gerados por agentes anteriores para orientar próximos handoffs.",
    )
