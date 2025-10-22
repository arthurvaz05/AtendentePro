#!/usr/bin/env python3
"""
Testes para Input Guardrails do AtendentePro
Verifica se os guardrails bloqueiam adequadamente entradas inadequadas
"""

import pytest
import json
from unittest.mock import Mock
from agents import ToolInputGuardrailData, ToolGuardrailFunctionOutput

# Importar os guardrails
from AtendentePro.guardrails import (
    reject_sensitive_content,
    reject_off_topic_queries,
    validate_iva_codes,
    detect_spam_patterns,
    get_guardrails_for_agent,
)


class TestGuardrails:
    """Testes para o sistema de guardrails"""

    def create_mock_data(self, tool_arguments: str) -> ToolInputGuardrailData:
        """Cria dados mock para teste"""
        mock_context = Mock()
        mock_context.tool_arguments = tool_arguments
        
        mock_data = Mock()
        mock_data.context = mock_context
        return mock_data

    def test_reject_sensitive_content(self):
        """Testa bloqueio de conteúdo sensível"""
        
        # Teste com palavra sensível
        sensitive_args = json.dumps({"query": "Como hackear o sistema?"})
        data = self.create_mock_data(sensitive_args)
        result = reject_sensitive_content(data)
        
        assert result.output_info is None  # Deve ser rejeitado
        assert "hack" in str(result.message).lower()
        
        # Teste com entrada válida
        valid_args = json.dumps({"query": "Qual o código IVA para energia?"})
        data = self.create_mock_data(valid_args)
        result = reject_sensitive_content(data)
        
        assert result.output_info == "Entrada validada com sucesso"

    def test_reject_off_topic_queries(self):
        """Testa bloqueio de consultas fora do escopo"""
        
        # Teste com tópico fora do escopo
        off_topic_args = json.dumps({"query": "quem descobriu o brasil?"})
        data = self.create_mock_data(off_topic_args)
        result = reject_off_topic_queries(data)
        
        assert result.output_info is None  # Deve ser rejeitado
        assert "brasil" in str(result.message).lower()
        
        # Teste com entrada válida
        valid_args = json.dumps({"query": "Qual o código IVA para energia elétrica?"})
        data = self.create_mock_data(valid_args)
        result = reject_off_topic_queries(data)
        
        assert result.output_info == "Consulta dentro do escopo válido"

    def test_validate_iva_codes(self):
        """Testa validação de códigos IVA"""
        
        # Teste com código IVA inválido
        invalid_args = json.dumps({"query": "Código IVA 99 para energia"})
        data = self.create_mock_data(invalid_args)
        result = validate_iva_codes(data)
        
        assert result.output_info is None  # Deve ser rejeitado
        assert "99" in str(result.message)
        
        # Teste com código IVA válido
        valid_args = json.dumps({"query": "Código IVA 15 para energia"})
        data = self.create_mock_data(valid_args)
        result = validate_iva_codes(data)
        
        assert result.output_info == "Códigos IVA validados"

    def test_detect_spam_patterns(self):
        """Testa detecção de padrões de spam"""
        
        # Teste com repetição excessiva
        spam_args = json.dumps({"query": "aaaaa"})
        data = self.create_mock_data(spam_args)
        result = detect_spam_patterns(data)
        
        assert result.output_info is None  # Deve ser rejeitado
        assert "spam" in str(result.message).lower()
        
        # Teste com mensagem muito curta
        short_args = json.dumps({"query": "oi"})
        data = self.create_mock_data(short_args)
        result = detect_spam_patterns(data)
        
        assert result.output_info is None  # Deve ser rejeitado
        assert "curta" in str(result.message).lower()
        
        # Teste com entrada válida
        valid_args = json.dumps({"query": "Qual o código IVA para energia elétrica?"})
        data = self.create_mock_data(valid_args)
        result = detect_spam_patterns(data)
        
        assert result.output_info == "Padrões de spam verificados"

    def test_get_guardrails_for_agent(self):
        """Testa mapeamento de guardrails por agente"""
        
        # Teste Triage Agent
        triage_guardrails = get_guardrails_for_agent("Triage Agent")
        assert len(triage_guardrails) == 2
        assert reject_off_topic_queries in triage_guardrails
        assert detect_spam_patterns in triage_guardrails
        
        # Teste Flow Agent
        flow_guardrails = get_guardrails_for_agent("Flow Agent")
        assert len(flow_guardrails) == 2
        assert reject_off_topic_queries in flow_guardrails
        assert validate_iva_codes in flow_guardrails
        
        # Teste Interview Agent
        interview_guardrails = get_guardrails_for_agent("Interview Agent")
        assert len(interview_guardrails) == 2
        assert reject_sensitive_content in interview_guardrails
        assert validate_iva_codes in interview_guardrails
        
        # Teste agente não mapeado (deve retornar padrão)
        unknown_guardrails = get_guardrails_for_agent("Unknown Agent")
        assert len(unknown_guardrails) == 1
        assert reject_sensitive_content in unknown_guardrails


class TestGuardrailsIntegration:
    """Testes de integração dos guardrails"""

    def test_brasil_question_blocked(self):
        """Testa especificamente a pergunta 'quem descobriu o brasil?'"""
        
        # Esta pergunta deve ser bloqueada por estar fora do escopo
        brasil_args = json.dumps({"query": "quem descobriu o brasil?"})
        data = Mock()
        data.context = Mock()
        data.context.tool_arguments = brasil_args
        
        result = reject_off_topic_queries(data)
        
        # Deve ser bloqueado
        assert result.output_info is None
        assert "brasil" in str(result.message).lower()
        assert "fora do escopo" in str(result.message).lower()

    def test_cryptocurrency_blocked(self):
        """Testa bloqueio de perguntas sobre criptomoedas"""
        
        crypto_args = json.dumps({"query": "Qual o código IVA para bitcoin?"})
        data = Mock()
        data.context = Mock()
        data.context.tool_arguments = crypto_args
        
        result = reject_off_topic_queries(data)
        
        # Deve ser bloqueado
        assert result.output_info is None
        assert "bitcoin" in str(result.message).lower()

    def test_valid_energy_question_allowed(self):
        """Testa que perguntas válidas sobre energia são permitidas"""
        
        energy_args = json.dumps({"query": "Qual o código IVA para energia elétrica?"})
        data = Mock()
        data.context = Mock()
        data.context.tool_arguments = energy_args
        
        # Testar todos os guardrails
        sensitive_result = reject_sensitive_content(data)
        topic_result = reject_off_topic_queries(data)
        iva_result = validate_iva_codes(data)
        spam_result = detect_spam_patterns(data)
        
        # Todos devem permitir
        assert sensitive_result.output_info == "Entrada validada com sucesso"
        assert topic_result.output_info == "Consulta dentro do escopo válido"
        assert iva_result.output_info == "Códigos IVA validados"
        assert spam_result.output_info == "Padrões de spam verificados"


if __name__ == "__main__":
    # Executar testes básicos
    test_instance = TestGuardrails()
    
    print("🧪 Executando testes de guardrails...")
    
    try:
        test_instance.test_reject_sensitive_content()
        print("✅ Teste de conteúdo sensível passou")
        
        test_instance.test_reject_off_topic_queries()
        print("✅ Teste de tópicos fora do escopo passou")
        
        test_instance.test_validate_iva_codes()
        print("✅ Teste de validação de códigos IVA passou")
        
        test_instance.test_detect_spam_patterns()
        print("✅ Teste de detecção de spam passou")
        
        test_instance.test_get_guardrails_for_agent()
        print("✅ Teste de mapeamento de guardrails passou")
        
        # Teste de integração
        integration_test = TestGuardrailsIntegration()
        integration_test.test_brasil_question_blocked()
        print("✅ Teste específico da pergunta 'brasil' passou")
        
        integration_test.test_valid_energy_question_allowed()
        print("✅ Teste de pergunta válida sobre energia passou")
        
        print("\n🎉 Todos os testes passaram!")
        print("🛡️ Sistema de guardrails funcionando corretamente")
        
    except Exception as e:
        print(f"❌ Teste falhou: {e}")
        raise
