#!/usr/bin/env python3
"""
Teste dos Guardrails com Validação de Tópicos e Códigos IVA
Testa especificamente a validação de códigos por tópico
"""

import json
import re
import yaml
from unittest.mock import Mock
from pathlib import Path

# Simular a classe GuardrailConfig para teste
class TestGuardrailConfig:
    """Configuração de teste para guardrails com tópicos"""
    
    def __init__(self):
        self.config = self._load_test_config()
    
    def _load_test_config(self):
        """Carrega configuração de teste com tópicos"""
        return {
            "topics": {
                "compra_industrializacao": {
                    "description": "Compra para industrialização — material manufaturado ou processo produtivo",
                    "codes": ["I0", "ID", "IE", "I8", "I5", "I9", "I2", "I7", "I1", "I3", "I4"]
                },
                "compra_comercializacao": {
                    "description": "Compra para comercialização — produto para revenda sem alteração",
                    "codes": ["R0", "ID", "R6", "R1", "R5", "R3", "R2", "R4"]
                },
                "aquisicao_energia_eletrica": {
                    "description": "Aquisição de energia elétrica — produtiva vs administrativa",
                    "codes": ["E1", "E2", "E3", "E4", "E0"]
                }
            },
            "valid_codes": ["I0", "ID", "IE", "R0", "R1", "E1", "E2"],  # Lista consolidada
            "off_topic_keywords": ["brasil", "bitcoin", "futebol"],
            "sensitive_words": ["hack", "fraude", "sonegação"]
        }
    
    def get_topics(self):
        return self.config.get("topics", {})
    
    def get_codes_for_topic(self, topic_name: str):
        topics = self.get_topics()
        if topic_name in topics:
            return topics[topic_name].get("codes", [])
        return []
    
    def get_all_valid_codes_from_topics(self):
        all_codes = []
        topics = self.get_topics()
        for topic_data in topics.values():
            all_codes.extend(topic_data.get("codes", []))
        return list(set(all_codes))
    
    def get_valid_codes(self):
        return self.config.get("valid_codes", [])

# Instância de teste
test_config = TestGuardrailConfig()

def validate_business_codes(data):
    """Valida códigos IVA - versão genérica"""
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return Mock(output_info="Argumentos JSON inválidos")

    # Usar códigos dos tópicos se disponível
    valid_codes = test_config.get_all_valid_codes_from_topics()
    if not valid_codes:
        valid_codes = test_config.get_valid_codes()
    
    if not valid_codes:
        return Mock(output_info="Validação de códigos não configurada")

    for key, value in args.items():
        value_str = str(value)
        
        # Procurar por códigos IVA no texto
        code_pattern = r'\b([A-Za-z]\d|[A-Za-z]{2})\b'  # Aceitar maiúsculas e minúsculas
        matches = re.findall(code_pattern, value_str)
        matches = [match.upper() for match in matches]  # Converter para maiúsculas
        
        for match in matches:
            if match not in valid_codes:
                return Mock(
                    output_info=None,
                    message=f"🚨 Código IVA inválido: '{match}' não é um código válido"
                )

    return Mock(output_info="Códigos IVA validados")

def validate_topic_and_codes(data):
    """Valida tópicos e códigos específicos por tópico"""
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return Mock(output_info="Argumentos JSON inválidos")

    topics = test_config.get_topics()
    
    if not topics:
        return Mock(output_info="Validação de tópicos não configurada")

    for key, value in args.items():
        value_str = str(value).lower()
        
        # Procurar por códigos IVA no texto
        code_pattern = r'\b([A-Za-z]\d|[A-Za-z]{2})\b'  # Aceitar maiúsculas e minúsculas
        matches = re.findall(code_pattern, value_str)
        matches = [match.upper() for match in matches]  # Converter para maiúsculas
        
        if matches:
            # Para cada código encontrado, verificar se está no tópico correto
            for code in matches:
                code_found_in_topic = False
                topic_for_code = None
                
                # Encontrar em qual tópico o código está
                for topic_name, topic_data in topics.items():
                    if code in topic_data.get("codes", []):
                        code_found_in_topic = True
                        topic_for_code = topic_name
                        break
                
                if not code_found_in_topic:
                    return Mock(
                        output_info=None,
                        message=f"🚨 Código IVA '{code}' não encontrado em nenhum tópico válido"
                    )
                
                # Verificar se o contexto da pergunta corresponde ao tópico do código
                topic_keywords = {
                    "compra_industrializacao": ["industrialização", "industrial", "produção", "manufaturado"],
                    "compra_comercializacao": ["comercialização", "revenda", "comercial"],
                    "aquisicao_energia_eletrica": ["energia", "elétrica", "eletricidade"]
                }
                
                # Verificar se o contexto da pergunta corresponde ao tópico
                context_matches = False
                if topic_for_code in topic_keywords:
                    for keyword in topic_keywords[topic_for_code]:
                        if keyword in value_str:
                            context_matches = True
                            break
                
                if not context_matches:
                    topic_description = topics[topic_for_code].get("description", "")
                    return Mock(
                        output_info=None,
                        message=f"🚨 Código IVA '{code}' não corresponde ao contexto da pergunta. Este código é para: {topic_description}"
                    )

    return Mock(output_info="Tópicos e códigos validados")

def test_valid_iva_code():
    """Testa código IVA válido"""
    
    print("🧪 TESTE: Código IVA Válido")
    print("=" * 50)
    print("Pergunta: 'Qual o código IVA I0 para industrialização?'")
    print("=" * 50)
    
    # Simular dados de entrada com código válido
    valid_args = '{"query": "Qual o código IVA I0 para industrialização?"}'
    
    # Criar mock data
    mock_data = Mock()
    mock_data.context = Mock()
    mock_data.context.tool_arguments = valid_args
    
    # Testar guardrail
    result = validate_business_codes(mock_data)
    
    print(f"Resultado: {result}")
    print(f"Permitido: {result.output_info is not None}")
    print(f"Mensagem: {result.output_info}")
    
    if result.output_info is not None:
        print("✅ Código IVA válido permitido!")
        return True
    else:
        print("❌ Código IVA válido foi bloqueado!")
        return False

def test_invalid_iva_code():
    """Testa código IVA inválido"""
    
    print("\n" + "=" * 50)
    print("TESTE: Código IVA Inválido")
    print("=" * 50)
    print("Pergunta: 'Qual o código IVA Z9 para industrialização?'")
    print("=" * 50)
    
    # Simular dados de entrada com código inválido
    invalid_args = '{"query": "Qual o código IVA Z9 para industrialização?"}'
    
    # Criar mock data
    mock_data = Mock()
    mock_data.context = Mock()
    mock_data.context.tool_arguments = invalid_args
    
    # Testar guardrail
    result = validate_business_codes(mock_data)
    
    print(f"Resultado: {result}")
    print(f"Bloqueado: {result.output_info is None}")
    print(f"Mensagem: {result.message}")
    
    if result.output_info is None:
        print("✅ Código IVA inválido bloqueado!")
        return True
    else:
        print("❌ Código IVA inválido foi permitido!")
        return False

def test_topic_context_validation():
    """Testa validação de contexto por tópico"""
    
    print("\n" + "=" * 50)
    print("TESTE: Validação de Contexto por Tópico")
    print("=" * 50)
    print("Pergunta: 'Qual o código IVA E1 para futebol?'")
    print("Código E1 é para energia elétrica, mas contexto é futebol")
    print("=" * 50)
    
    # Simular dados de entrada com código correto mas contexto errado
    context_mismatch_args = '{"query": "Qual o código IVA E1 para futebol?"}'
    
    # Criar mock data
    mock_data = Mock()
    mock_data.context = Mock()
    mock_data.context.tool_arguments = context_mismatch_args
    
    # Testar guardrail
    result = validate_topic_and_codes(mock_data)
    
    print(f"Resultado: {result}")
    print(f"Bloqueado: {result.output_info is None}")
    print(f"Mensagem: {result.message}")
    
    if result.output_info is None:
        print("✅ Contexto incompatível bloqueado!")
        return True
    else:
        print("❌ Contexto incompatível foi permitido!")
        return False

def test_topic_context_correct():
    """Testa validação de contexto correto"""
    
    print("\n" + "=" * 50)
    print("TESTE: Contexto Correto")
    print("=" * 50)
    print("Pergunta: 'Qual o código IVA E1 para energia elétrica?'")
    print("Código E1 é para energia elétrica, contexto também é energia")
    print("=" * 50)
    
    # Simular dados de entrada com código e contexto corretos
    correct_context_args = '{"query": "Qual o código IVA E1 para energia elétrica?"}'
    
    # Criar mock data
    mock_data = Mock()
    mock_data.context = Mock()
    mock_data.context.tool_arguments = correct_context_args
    
    # Testar guardrail
    result = validate_topic_and_codes(mock_data)
    
    print(f"Resultado: {result}")
    print(f"Permitido: {result.output_info is not None}")
    print(f"Mensagem: {result.output_info}")
    
    if result.output_info is not None:
        print("✅ Contexto correto permitido!")
        return True
    else:
        print("❌ Contexto correto foi bloqueado!")
        return False

def test_topics_structure():
    """Testa estrutura de tópicos"""
    
    print("\n" + "=" * 50)
    print("TESTE: Estrutura de Tópicos")
    print("=" * 50)
    
    topics = test_config.get_topics()
    
    print(f"✅ Tópicos carregados: {len(topics)}")
    for topic_name, topic_data in topics.items():
        codes = topic_data.get("codes", [])
        description = topic_data.get("description", "")
        print(f"   - {topic_name}: {len(codes)} códigos")
        print(f"     Descrição: {description[:50]}...")
        print(f"     Códigos: {codes[:3]}...")
    
    # Verificar códigos específicos
    industrial_codes = test_config.get_codes_for_topic("compra_industrializacao")
    energy_codes = test_config.get_codes_for_topic("aquisicao_energia_eletrica")
    
    assert "I0" in industrial_codes, "Código I0 deveria estar em industrialização"
    assert "E1" in energy_codes, "Código E1 deveria estar em energia elétrica"
    
    print("✅ Estrutura de tópicos carregada corretamente!")
    return True

if __name__ == "__main__":
    print("🛡️ TESTE COMPLETO DOS GUARDRAILS COM TÓPICOS")
    print("=" * 80)
    
    # Executar todos os testes
    test1 = test_valid_iva_code()
    test2 = test_invalid_iva_code()
    test3 = test_topic_context_validation()
    test4 = test_topic_context_correct()
    test5 = test_topics_structure()
    
    print("\n" + "=" * 80)
    print("📋 RESUMO DOS TESTES")
    print("=" * 80)
    print(f"✅ Código IVA válido permitido: {'SIM' if test1 else 'NÃO'}")
    print(f"✅ Código IVA inválido bloqueado: {'SIM' if test2 else 'NÃO'}")
    print(f"✅ Contexto incompatível bloqueado: {'SIM' if test3 else 'NÃO'}")
    print(f"✅ Contexto correto permitido: {'SIM' if test4 else 'NÃO'}")
    print(f"✅ Estrutura de tópicos carregada: {'SIM' if test5 else 'NÃO'}")
    
    if test1 and test2 and test3 and test4 and test5:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("🛡️ Sistema de guardrails com tópicos funcionando corretamente")
        print("📁 Validação de códigos por tópico implementada")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        print("🔧 Sistema de guardrails precisa de ajustes")
    
    print("=" * 80)
