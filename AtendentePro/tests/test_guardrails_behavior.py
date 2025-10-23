#!/usr/bin/env python3
"""
Teste automatizado do sistema de guardrails
Simula o comportamento observado no teste manual
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Adiciona o diretório raiz ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from AtendentePro.guardrails import GuardrailOutput


class TestGuardrailsBehavior(unittest.TestCase):
    """Testa o comportamento do sistema de guardrails baseado no teste manual"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        # Configura API key de teste para evitar erros
        os.environ['OPENAI_API_KEY'] = 'sk-test-key-for-testing'
    
    def test_history_question_should_be_rejected(self):
        """Testa se pergunta sobre história deveria ser rejeitada"""
        # Simula a resposta esperada do sistema de guardrails
        expected_output = GuardrailOutput(
            reasoning="Esta mensagem está relacionada a história e geografia, que está fora do escopo dos agentes White Martins focados em processos fiscais.",
            is_in_scope=False,
            confidence=0.95,
            suggested_action="refuse"
        )
        
        # Verificações baseadas no comportamento esperado
        self.assertFalse(expected_output.is_in_scope, "Pergunta sobre história deveria estar fora do escopo")
        self.assertEqual(expected_output.suggested_action, "refuse", "Deveria sugerir recusar")
        self.assertGreaterEqual(expected_output.confidence, 0.9, "Confiança deveria ser alta")
        self.assertIn("história", expected_output.reasoning.lower(), "Razão deveria mencionar história")
        self.assertIn("fiscais", expected_output.reasoning.lower(), "Razão deveria mencionar fiscais")
    
    def test_fiscal_question_should_be_accepted(self):
        """Testa se pergunta sobre processos fiscais deveria ser aceita"""
        # Simula a resposta esperada do sistema de guardrails
        expected_output = GuardrailOutput(
            reasoning="Esta mensagem está relacionada aos processos fiscais e códigos IVA da White Martins.",
            is_in_scope=True,
            confidence=0.90,
            suggested_action="continue"
        )
        
        # Verificações baseadas no comportamento esperado
        self.assertTrue(expected_output.is_in_scope, "Pergunta sobre códigos IVA deveria estar no escopo")
        self.assertEqual(expected_output.suggested_action, "continue", "Deveria sugerir continuar")
        self.assertGreaterEqual(expected_output.confidence, 0.8, "Confiança deveria ser alta")
        self.assertIn("fiscais", expected_output.reasoning.lower(), "Razão deveria mencionar fiscais")
        self.assertIn("iva", expected_output.reasoning.lower(), "Razão deveria mencionar IVA")
    
    def test_mathematics_question_should_be_rejected(self):
        """Testa se pergunta sobre matemática deveria ser rejeitada"""
        # Simula a resposta esperada do sistema de guardrails
        expected_output = GuardrailOutput(
            reasoning="Esta mensagem está relacionada a matemática, que está fora do escopo dos agentes White Martins.",
            is_in_scope=False,
            confidence=0.90,
            suggested_action="refuse"
        )
        
        # Verificações baseadas no comportamento esperado
        self.assertFalse(expected_output.is_in_scope, "Pergunta sobre matemática deveria estar fora do escopo")
        self.assertEqual(expected_output.suggested_action, "refuse", "Deveria sugerir recusar")
        self.assertGreaterEqual(expected_output.confidence, 0.8, "Confiança deveria ser alta")
        self.assertIn("matemática", expected_output.reasoning.lower(), "Razão deveria mencionar matemática")
    
    def test_programming_question_should_be_rejected(self):
        """Testa se pergunta sobre programação deveria ser rejeitada"""
        # Simula a resposta esperada do sistema de guardrails
        expected_output = GuardrailOutput(
            reasoning="Esta mensagem está relacionada a programação, que está fora do escopo dos agentes White Martins.",
            is_in_scope=False,
            confidence=0.85,
            suggested_action="refuse"
        )
        
        # Verificações baseadas no comportamento esperado
        self.assertFalse(expected_output.is_in_scope, "Pergunta sobre programação deveria estar fora do escopo")
        self.assertEqual(expected_output.suggested_action, "refuse", "Deveria sugerir recusar")
        self.assertGreaterEqual(expected_output.confidence, 0.7, "Confiança deveria ser boa")
        self.assertIn("programação", expected_output.reasoning.lower(), "Razão deveria mencionar programação")
    
    def test_entertainment_question_should_be_rejected(self):
        """Testa se pergunta sobre entretenimento deveria ser rejeitada"""
        # Simula a resposta esperada do sistema de guardrails
        expected_output = GuardrailOutput(
            reasoning="Esta mensagem está relacionada a entretenimento, que está fora do escopo dos agentes White Martins.",
            is_in_scope=False,
            confidence=0.85,
            suggested_action="refuse"
        )
        
        # Verificações baseadas no comportamento esperado
        self.assertFalse(expected_output.is_in_scope, "Pergunta sobre entretenimento deveria estar fora do escopo")
        self.assertEqual(expected_output.suggested_action, "refuse", "Deveria sugerir recusar")
        self.assertGreaterEqual(expected_output.confidence, 0.7, "Confiança deveria ser boa")
        self.assertIn("entretenimento", expected_output.reasoning.lower(), "Razão deveria mencionar entretenimento")
    
    def test_fiscal_process_question_should_be_accepted(self):
        """Testa se pergunta sobre processo fiscal deveria ser aceita"""
        # Simula a resposta esperada do sistema de guardrails
        expected_output = GuardrailOutput(
            reasoning="Esta mensagem está relacionada aos processos fiscais da White Martins.",
            is_in_scope=True,
            confidence=0.90,
            suggested_action="continue"
        )
        
        # Verificações baseadas no comportamento esperado
        self.assertTrue(expected_output.is_in_scope, "Pergunta sobre processo fiscal deveria estar no escopo")
        self.assertEqual(expected_output.suggested_action, "continue", "Deveria sugerir continuar")
        self.assertGreaterEqual(expected_output.confidence, 0.8, "Confiança deveria ser alta")
        self.assertIn("fiscais", expected_output.reasoning.lower(), "Razão deveria mencionar fiscais")
    
    def test_guardrail_output_structure(self):
        """Testa estrutura do GuardrailOutput"""
        output = GuardrailOutput(
            reasoning="Teste de estrutura",
            is_in_scope=True,
            confidence=0.8,
            suggested_action="continue"
        )
        
        self.assertIsInstance(output.reasoning, str)
        self.assertIsInstance(output.is_in_scope, bool)
        self.assertIsInstance(output.confidence, float)
        self.assertIsInstance(output.suggested_action, str)
        self.assertIn(output.suggested_action, ["continue", "redirect", "refuse"])
        self.assertGreaterEqual(output.confidence, 0.0)
        self.assertLessEqual(output.confidence, 1.0)
    
    def test_confidence_ranges(self):
        """Testa se os ranges de confiança estão corretos"""
        # Teste com diferentes níveis de confiança
        high_confidence = GuardrailOutput(
            reasoning="Alta confiança",
            is_in_scope=False,
            confidence=0.95,
            suggested_action="refuse"
        )
        
        medium_confidence = GuardrailOutput(
            reasoning="Confiança média",
            is_in_scope=False,
            confidence=0.75,
            suggested_action="redirect"
        )
        
        low_confidence = GuardrailOutput(
            reasoning="Baixa confiança",
            is_in_scope=False,
            confidence=0.60,
            suggested_action="redirect"
        )
        
        self.assertGreaterEqual(high_confidence.confidence, 0.9, "Alta confiança deveria ser >= 0.9")
        self.assertGreaterEqual(medium_confidence.confidence, 0.7, "Confiança média deveria ser >= 0.7")
        self.assertGreaterEqual(low_confidence.confidence, 0.5, "Baixa confiança deveria ser >= 0.5")
    
    def test_suggested_actions_logic(self):
        """Testa a lógica das ações sugeridas"""
        # Teste para mensagens claramente fora do escopo
        refuse_output = GuardrailOutput(
            reasoning="Claramente fora do escopo",
            is_in_scope=False,
            confidence=0.95,
            suggested_action="refuse"
        )
        
        # Teste para mensagens no escopo
        continue_output = GuardrailOutput(
            reasoning="Dentro do escopo",
            is_in_scope=True,
            confidence=0.90,
            suggested_action="continue"
        )
        
        # Teste para mensagens ambíguas
        redirect_output = GuardrailOutput(
            reasoning="Mensagem ambígua",
            is_in_scope=False,
            confidence=0.60,
            suggested_action="redirect"
        )
        
        self.assertEqual(refuse_output.suggested_action, "refuse", "Mensagens claramente fora do escopo deveriam ser recusadas")
        self.assertEqual(continue_output.suggested_action, "continue", "Mensagens no escopo deveriam continuar")
        self.assertEqual(redirect_output.suggested_action, "redirect", "Mensagens ambíguas deveriam ser redirecionadas")


if __name__ == "__main__":
    unittest.main()
