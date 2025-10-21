"""Testes para configurações do sistema."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure project and package roots are on sys.path for absolute imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

PACKAGE_ROOT = PROJECT_ROOT / "AtendentePro"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.append(str(PACKAGE_ROOT))

import config  # noqa: E402


def test_config_variables_exist():
    """Testa se todas as variáveis de configuração existem."""
    for attr in (
        "OPENAI_PROVIDER",
        "OPENAI_API_KEY",
        "AZURE_API_KEY",
        "AZURE_API_ENDPOINT",
        "AZURE_API_VERSION",
        "APPLICATION_INSIGHTS_CONNECTION_STRING",
        "CONTEXT_OUTPUT_DIR",
        "DEFAULT_MODEL",
        "RECOMMENDED_PROMPT_PREFIX",
    ):
        assert hasattr(config, attr)


def test_provider_selection():
    """Garante que o provider configurado é suportado e possui credenciais."""
    assert config.OPENAI_PROVIDER in ("azure", "openai")

    if config.OPENAI_PROVIDER == "azure":
        assert isinstance(config.AZURE_API_KEY, str)
        assert isinstance(config.AZURE_API_ENDPOINT, str)
        assert isinstance(config.AZURE_API_VERSION, str)
        assert config.AZURE_API_KEY.strip()
        assert config.AZURE_API_ENDPOINT.strip()
        assert config.AZURE_API_VERSION.strip()
    else:
        assert isinstance(config.OPENAI_API_KEY, str)
        assert config.OPENAI_API_KEY.startswith("sk-")


def test_context_output_dir():
    """Testa se o diretório de contexto está configurado."""
    context_dir = config.CONTEXT_OUTPUT_DIR
    assert isinstance(context_dir, str)
    assert len(context_dir) > 0


def test_default_model():
    """Testa se o modelo padrão está configurado."""
    model = config.DEFAULT_MODEL
    assert isinstance(model, str)
    assert len(model) > 0
    # Verifica se é um modelo válido
    assert 'gpt' in model.lower()


def test_recommended_prompt_prefix():
    """Testa se o prefixo de prompt está configurado."""
    prefix = config.RECOMMENDED_PROMPT_PREFIX
    assert isinstance(prefix, str)
    assert len(prefix) > 0
    # Verifica se contém informações sobre o sistema multiagente
    assert 'multiagente' in prefix.lower() or 'agent' in prefix.lower()


def test_environment_variable_set():
    """Testa se a variável de ambiente do provider escolhido está definida."""
    if config.OPENAI_PROVIDER == "azure":
        assert os.getenv('AZURE_API_KEY') is not None
        assert os.getenv('AZURE_API_KEY') == config.AZURE_API_KEY
    else:
        assert os.getenv('OPENAI_API_KEY') is not None
        assert os.getenv('OPENAI_API_KEY') == config.OPENAI_API_KEY


def test_application_insights_config_is_str_or_none():
    """Verifica se a connection string do Application Insights é string ou None."""
    value = config.APPLICATION_INSIGHTS_CONNECTION_STRING
    assert value is None or isinstance(value, str)
