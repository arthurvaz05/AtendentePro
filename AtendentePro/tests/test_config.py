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
    assert hasattr(config, 'OPENAI_API_KEY')
    assert hasattr(config, 'CONTEXT_OUTPUT_DIR')
    assert hasattr(config, 'DEFAULT_MODEL')
    assert hasattr(config, 'RECOMMENDED_PROMPT_PREFIX')


def test_openai_api_key_format():
    """Testa se a API key tem o formato correto."""
    api_key = config.OPENAI_API_KEY
    assert isinstance(api_key, str)
    assert len(api_key) > 0
    # OpenAI API keys geralmente começam com 'sk-'
    assert api_key.startswith('sk-')


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
    """Testa se a variável de ambiente OPENAI_API_KEY está definida."""
    assert os.getenv('OPENAI_API_KEY') is not None
    assert os.getenv('OPENAI_API_KEY') == config.OPENAI_API_KEY
