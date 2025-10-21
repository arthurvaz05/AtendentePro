from __future__ import annotations

import json
from typing import Any

from agents.result import RunResult

from AtendentePro.context import ContextNote


def _serialize_output(output: Any) -> Any:
    """Convert agent outputs into JSON-serialisable data."""
    if output is None:
        return {}
    if hasattr(output, "model_dump"):
        try:
            return output.model_dump()
        except TypeError:
            return output.model_dump(exclude_none=True)  # type: ignore[misc]
    if hasattr(output, "dict"):
        return output.dict()  # type: ignore[call-arg]
    if isinstance(output, (dict, list, str, int, float, bool)):
        return output
    return {"value": repr(output)}


def append_handoff_summary(
    result: RunResult,
    context: ContextNote,
    payload_key: str,
    next_agent_hint: str | None = None,
    summary_label: str | None = None,
) -> list[dict[str, Any]]:
    """
    Persist a structured payload on the shared context and append a handoff summary
    message to the transcript so the next agent has immediate access to it.
    """

    payload = _serialize_output(result.final_output)
    from_agent = result.last_agent.name
    target_agent = next_agent_hint or from_agent
    label = summary_label or payload_key

    context.handoff_summaries[label] = {
        "from_agent": from_agent,
        "next_agent_hint": target_agent,
        "payload_key": payload_key,
        "payload": payload,
    }

    summary_lines = [
        "[HANDOFF_SUMMARY]",
        f"from_agent: {from_agent}",
        f"payload_key: {payload_key}",
    ]
    if target_agent:
        summary_lines.append(f"next_agent: {target_agent}")
    summary_lines.append(f"payload: {json.dumps(payload, ensure_ascii=False)}")
    summary_lines.append("[/HANDOFF_SUMMARY]")

    updated_input_items = result.to_input_list()
    updated_input_items.append(
        {
            "role": "assistant",
            "content": "\n".join(summary_lines),
        }
    )
    return updated_input_items
