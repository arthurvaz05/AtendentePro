from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx
from agents import tracing
from agents.tracing.processor_interface import TracingExporter
from agents.tracing.processors import BatchTraceProcessor
from agents.tracing.spans import Span
from agents.tracing.traces import Trace

from AtendentePro import config

logger = logging.getLogger(__name__)


@dataclass
class _ConnectionInfo:
    instrumentation_key: str
    endpoint_url: str


def _parse_connection_string(value: str) -> _ConnectionInfo:
    parts = {}
    for segment in value.split(";"):
        segment = segment.strip()
        if not segment or "=" not in segment:
            continue
        key, val = segment.split("=", 1)
        parts[key.strip().lower()] = val.strip()

    instrumentation_key = parts.get("instrumentationkey")
    if not instrumentation_key:
        raise ValueError("InstrumentationKey ausente no Application Insights connection string.")

    ingestion_endpoint = parts.get("ingestionendpoint", "https://dc.services.visualstudio.com")
    ingestion_endpoint = ingestion_endpoint.rstrip("/") + "/v2/track"

    return _ConnectionInfo(instrumentation_key=instrumentation_key, endpoint_url=ingestion_endpoint)


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:  # noqa: BLE001
        return repr(value)


class ApplicationInsightsExporter(TracingExporter):
    """Exports Agent SDK traces to Azure Application Insights."""

    def __init__(self, connection_string: str):
        info = _parse_connection_string(connection_string)
        self._ikey = info.instrumentation_key
        self._endpoint = info.endpoint_url
        self._client = httpx.Client(timeout=httpx.Timeout(timeout=30.0, connect=5.0))

    def export(self, items: list["Trace | Span[Any]"]) -> None:
        envelopes = [env for env in (_convert_item(self._ikey, item) for item in items) if env]
        if not envelopes:
            return

        try:
            response = self._client.post(self._endpoint, json=envelopes)
            if response.status_code >= 300:
                logger.error(
                    "Falha ao exportar traces para Application Insights (%s): %s",
                    response.status_code,
                    response.text,
                )
        except Exception as exc:  # noqa: BLE001
            logger.error("Erro ao enviar traces para Application Insights: %s", exc, exc_info=True)

    def close(self) -> None:
        self._client.close()


class ApplicationInsightsTraceProcessor(BatchTraceProcessor):
    """Batch processor que garante o encerramento do exporter customizado."""

    def __init__(self, exporter: ApplicationInsightsExporter):
        super().__init__(exporter)
        self._exporter = exporter

    def shutdown(self, timeout: float | None = None):  # noqa: D401
        super().shutdown(timeout=timeout)
        self._exporter.close()


def _convert_item(instrumentation_key: str, item: "Trace | Span[Any]") -> dict[str, Any] | None:
    if isinstance(item, Trace):
        payload = item.export()
        if not payload:
            return None
        time = _iso_now()
        properties = {
            "trace_id": payload.get("id"),
            "workflow_name": payload.get("workflow_name"),
            "group_id": payload.get("group_id"),
            "metadata": _stringify(payload.get("metadata")),
            "event.name": "agents.trace",
        }
        message = f"Trace {payload.get('id')} - {payload.get('workflow_name')}"
        tags = {
            "ai.operation.id": payload.get("id"),
            "ai.operation.name": payload.get("workflow_name") or "",
        }
        return _build_envelope(instrumentation_key, time, message, properties, tags)

    if isinstance(item, Span):
        payload = item.export()
        if not payload:
            return None
        data = payload.get("span_data", {})
        started_at = payload.get("started_at")
        ended_at = payload.get("ended_at")
        time = ended_at or started_at or _iso_now()
        span_type = data.get("type") if isinstance(data, dict) else None

        event_name = "agents.span"
        if span_type == "generation":
            event_name = "gen_ai.choice"
        elif span_type == "agent":
            event_name = "gen_ai.agent"
        elif span_type == "response":
            event_name = "gen_ai.assistant.message"

        properties = {
            "trace_id": payload.get("trace_id"),
            "span_id": payload.get("id"),
            "parent_id": payload.get("parent_id"),
            "span_type": span_type,
            "span_payload": _stringify(data),
            "error": _stringify(payload.get("error")),
            "started_at": started_at,
            "ended_at": ended_at,
            "event.name": event_name,
            "gen_ai.provider.name": getattr(config, "OPENAI_PROVIDER", "azure"),
            "gen_ai.event.content": _stringify(data),
        }
        message = f"Span {payload.get('id')} ({span_type or 'span'})"
        tags = {
            "ai.operation.id": payload.get("trace_id"),
            "ai.operation.parentId": payload.get("parent_id") or payload.get("trace_id"),
        }
        return _build_envelope(instrumentation_key, time, message, properties, tags)

    return None


def _build_envelope(
    instrumentation_key: str,
    time_iso: str,
    message: str,
    properties: dict[str, Any],
    tags: dict[str, Any] | None = None,
) -> dict[str, Any]:
    filtered_props = {k: _stringify(v) for k, v in properties.items() if v not in (None, "")}
    envelope = {
        "name": "Microsoft.ApplicationInsights.Message",
        "time": time_iso,
        "iKey": instrumentation_key,
        "data": {
            "baseType": "MessageData",
            "baseData": {
                "message": message,
                "severityLevel": 1,
                "properties": filtered_props,
            },
        },
    }
    if tags:
        envelope["tags"] = {k: v for k, v in tags.items() if v}
    return envelope


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def configure_tracing() -> None:
    """Configure tracing export based on configuration."""
    connection_string = (
        getattr(config, "APPLICATION_INSIGHTS_CONNECTION_STRING", None) or ""
    ).strip()
    provider = getattr(config, "OPENAI_PROVIDER", "openai")

    if connection_string:
        try:
            exporter = ApplicationInsightsExporter(connection_string)
        except ValueError as exc:
            logger.error("Application Insights não configurado: %s", exc)
            tracing.set_trace_processors([])
            tracing.set_tracing_disabled(True)
            os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "true")
            return

        processor = ApplicationInsightsTraceProcessor(exporter)
        tracing.set_trace_processors([processor])
        tracing.set_tracing_disabled(False)
        logger.info("Tracing configurado para exportar via Application Insights.")
        os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "false")
        return

    if provider == "azure":
        tracing.set_trace_processors([])
        tracing.set_tracing_disabled(True)
        os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "true")
        logger.info("Tracing desativado para evitar exportação ao backend OpenAI.")
