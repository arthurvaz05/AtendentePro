"""Testes para o sistema de contexto."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project and package roots are on sys.path for absolute imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

PACKAGE_ROOT = PROJECT_ROOT / "AtendentePro"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.append(str(PACKAGE_ROOT))

from AtendentePro.context import ContextNote  # noqa: E402


def test_context_note_creation():
    """Testa a criação de um ContextNote."""
    context = ContextNote()
    assert isinstance(context, ContextNote)
    assert isinstance(context.handoff_summaries, dict)
    assert len(context.handoff_summaries) == 0


def test_context_note_with_data():
    """Testa ContextNote com dados iniciais."""
    initial_data = {
        "test_summary": {
            "from_agent": "Test Agent",
            "next_agent_hint": "Next Agent",
            "payload_key": "test_payload",
            "payload": {"test": "data"}
        }
    }
    context = ContextNote(handoff_summaries=initial_data)
    assert context.handoff_summaries == initial_data
    assert "test_summary" in context.handoff_summaries


def test_context_note_handoff_summaries_structure():
    """Testa a estrutura dos handoff_summaries."""
    context = ContextNote()
    
    # Adiciona um resumo de handoff
    context.handoff_summaries["test"] = {
        "from_agent": "Agent A",
        "next_agent_hint": "Agent B",
        "payload_key": "test_data",
        "payload": {"key": "value"}
    }
    
    summary = context.handoff_summaries["test"]
    assert summary["from_agent"] == "Agent A"
    assert summary["next_agent_hint"] == "Agent B"
    assert summary["payload_key"] == "test_data"
    assert summary["payload"] == {"key": "value"}


def test_context_note_multiple_summaries():
    """Testa ContextNote com múltiplos resumos."""
    context = ContextNote()
    
    # Adiciona múltiplos resumos
    context.handoff_summaries["summary1"] = {
        "from_agent": "Agent 1",
        "payload": {"data": "1"}
    }
    context.handoff_summaries["summary2"] = {
        "from_agent": "Agent 2", 
        "payload": {"data": "2"}
    }
    
    assert len(context.handoff_summaries) == 2
    assert "summary1" in context.handoff_summaries
    assert "summary2" in context.handoff_summaries
    assert context.handoff_summaries["summary1"]["payload"]["data"] == "1"
    assert context.handoff_summaries["summary2"]["payload"]["data"] == "2"


def test_context_note_immutability():
    """Testa se os dados do contexto podem ser modificados."""
    context = ContextNote()
    original_summaries = context.handoff_summaries
    
    # Modifica o dicionário
    context.handoff_summaries["new"] = {"test": "data"}
    
    # Verifica se a modificação foi persistida
    assert "new" in context.handoff_summaries
    assert context.handoff_summaries is original_summaries
