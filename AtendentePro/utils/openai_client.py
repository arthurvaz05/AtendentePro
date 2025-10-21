from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal, Union

from AtendentePro import config

if getattr(config, "OPENAI_PROVIDER", "openai") == "azure":
    _disable_flags = {
        "OPENAI_TRACE_DISABLED": "true",
        "OPENAI_TRACING_DISABLED": "true",
        "OPENAI_TELEMETRY_DISABLED": "true",
        "OPENAI_TRACE": "false",
        "OPENAI_TELEMETRY": "false",
        "OPENAI_TRACE_ENABLED": "false",
        "OPENAI_TRACING_ENABLED": "false",
        "OPENAI_TELEMETRY_ENABLED": "false",
        "OPENAI_DISABLE_TRACING": "true",
        "OPENAI_DISABLE_TELEMETRY": "true",
        "AGENTS_TRACE_DISABLED": "true",
        "OPENAI_AGENTS_TRACE_DISABLED": "true",
    }
    for key, value in _disable_flags.items():
        os.environ.setdefault(key, value)

from openai import AsyncAzureOpenAI, AsyncOpenAI

try:  # best effort: newer SDK exposes tracing helpers
    from openai import traces as _openai_traces  # type: ignore

    if hasattr(_openai_traces, "configure"):
        _openai_traces.configure(enabled=False)  # type: ignore[arg-type]
    elif hasattr(_openai_traces, "set_enabled"):
        _openai_traces.set_enabled(False)  # type: ignore[attr-defined]
    elif hasattr(_openai_traces, "disable"):
        _openai_traces.disable()  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001 - tracing API is optional
    pass

for _trace_module in (
    "agents.tracing",
    "agents.trace",
    "openai.agents.tracing",
    "openai.agents.trace",
):
    try:
        _mod = __import__(_trace_module, fromlist=["dummy"])
    except Exception:
        continue
    for attr in ("set_tracing_client", "configure", "set_enabled", "disable"):
        func = getattr(_mod, attr, None)
        try:
            if callable(func):
                if attr == "set_tracing_client":
                    func(None)
                elif attr == "configure":
                    func(enabled=False)  # type: ignore[arg-type]
                else:
                    func(False)  # type: ignore[arg-type]
        except Exception:
            pass

Provider = Literal["azure", "openai"]
AsyncClient = Union[AsyncAzureOpenAI, AsyncOpenAI]


def get_provider() -> Provider:
    """Return the configured provider, defaulting to the available credentials."""
    provider = getattr(config, "OPENAI_PROVIDER", "openai")
    if provider not in ("azure", "openai"):
        return "openai"
    return provider  # type: ignore[return-value]


@lru_cache(maxsize=1)
def get_async_client() -> AsyncClient:
    """Instantiate and cache the async OpenAI-compatible client."""
    provider = get_provider()

    if provider == "azure":
        required = {
            "AZURE_API_KEY": getattr(config, "AZURE_API_KEY", None),
            "AZURE_API_ENDPOINT": getattr(config, "AZURE_API_ENDPOINT", None),
            "AZURE_API_VERSION": getattr(config, "AZURE_API_VERSION", None),
        }
        missing = [name for name, value in required.items() if not value]

        if missing:
            names = ", ".join(missing)
            raise RuntimeError(f"Credenciais Azure OpenAI ausentes: {names}")

        client = AsyncAzureOpenAI(
            api_key=config.AZURE_API_KEY,
            azure_endpoint=config.AZURE_API_ENDPOINT,
            api_version=config.AZURE_API_VERSION,
        )

        # Configure default deployment if provided
        if getattr(config, "AZURE_DEPLOYMENT_NAME", None):
            client.azure_deployment = config.AZURE_DEPLOYMENT_NAME  # type: ignore[attr-defined]

        # Best effort: disable tracing hooks on the instantiated client
        try:
            traces_attr = getattr(client, "traces", None)
            if traces_attr is not None:
                if hasattr(traces_attr, "disable"):
                    traces_attr.disable()
                if hasattr(traces_attr, "set_enabled"):
                    traces_attr.set_enabled(False)  # type: ignore[attr-defined]
                setattr(client, "traces", None)
        except Exception:  # noqa: BLE001 - tracing API is optional
            pass

        return client

    if not getattr(config, "OPENAI_API_KEY", None):
        raise RuntimeError("OPENAI_API_KEY não configurada. Defina-a ou selecione provider=azure.")

    return AsyncOpenAI(api_key=config.OPENAI_API_KEY)
