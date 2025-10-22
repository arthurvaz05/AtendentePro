#!/usr/bin/env python3
"""
Teste das mensagens educativas dos guardrails
Verifica se os guardrails retornam mensagens amigáveis ao invés de exceções
"""

import sys
import os
from pathlib import Path
from unittest.mock import Mock

# Adicionar o diretório pai ao path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Importar módulos
from guardrails import (
    reject_off_topic_queries,
    reject_sensitive_content,
    validate_business_codes,
    detect_spam_patterns,
    reject_off_topic_queries_factory
)

def test_educational_messages():
    """Testa se os guardrails retornam mensagens educativas"""
    
    print("🧪 TESTE: Mensagens Educativas dos Guardrails")
    print("=" * 60)
    
    # Casos de teste para diferentes guardrails
    test_cases = [
        {
            "guardrail": "reject_off_topic_queries",
            "function": reject_off_topic_queries,
            "query": "quem descobriu o brasil?",
            "expected_keywords": ["Desculpe", "não posso responder", "reformule"]
        },
        {
            "guardrail": "reject_sensitive_content", 
            "function": reject_sensitive_content,
            "query": "como fazer fraude de IVA?",
            "expected_keywords": ["Desculpe", "conteúdo sensível", "reformule"]
        },
        {
            "guardrail": "validate_business_codes",
            "function": validate_business_codes,
            "query": "qual o código IVA Z9?",
            "expected_keywords": ["Desculpe", "código", "não é válido", "verifique"]
        },
        {
            "guardrail": "detect_spam_patterns",
            "function": detect_spam_patterns,
            "query": "aaaaa",
            "expected_keywords": ["Desculpe", "muito curta", "mais detalhes"]
        }
    ]
    
    success_count = 0
    
    for case in test_cases:
        print(f"\n📋 Testando: {case['guardrail']}")
        print(f"   Query: '{case['query']}'")
        print("-" * 40)
        
        # Simular dados
        args = f'{{"query": "{case["query"]}"}}'
        mock_data = Mock()
        mock_data.context = Mock()
        mock_data.context.tool_arguments = args
        
        try:
            # Executar guardrail
            result = case["function"](mock_data)
            
            # Verificar se retornou mensagem educativa
            if result.output_info:
                message = result.output_info
                print(f"   ✅ Mensagem: {message}")
                
                # Verificar se contém palavras-chave esperadas
                contains_expected = all(
                    keyword.lower() in message.lower() 
                    for keyword in case["expected_keywords"]
                )
                
                if contains_expected:
                    print(f"   ✅ Contém palavras educativas esperadas")
                    success_count += 1
                else:
                    print(f"   ❌ Não contém palavras educativas esperadas")
                    print(f"   Esperado: {case['expected_keywords']}")
            else:
                print(f"   ❌ Nenhuma mensagem retornada")
                
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
    
    print(f"\n📊 Resultado: {success_count}/{len(test_cases)} guardrails com mensagens educativas")
    return success_count == len(test_cases)

def test_agent_specific_messages():
    """Testa mensagens específicas por agente"""
    
    print("\n🧪 TESTE: Mensagens Específicas por Agente")
    print("=" * 60)
    
    agents_to_test = [
        "Confirmation Agent",
        "Knowledge Agent", 
        "Usage Agent"
    ]
    
    success_count = 0
    
    for agent_name in agents_to_test:
        print(f"\n📋 Testando: {agent_name}")
        print("-" * 40)
        
        # Criar guardrail específico do agente
        agent_guardrail = reject_off_topic_queries_factory(agent_name)
        
        # Simular dados com tema fora do escopo
        args = '{"query": "quem descobriu o brasil?"}'
        mock_data = Mock()
        mock_data.context = Mock()
        mock_data.context.tool_arguments = args
        
        try:
            # Executar guardrail específico do agente
            result = agent_guardrail(mock_data)
            
            if result.output_info:
                message = result.output_info
                print(f"   ✅ Mensagem: {message}")
                
                # Verificar se menciona o agente específico
                agent_friendly = agent_name.replace(" Agent", "").lower()
                if agent_friendly in message.lower():
                    print(f"   ✅ Menciona agente específico: {agent_friendly}")
                    success_count += 1
                else:
                    print(f"   ❌ Não menciona agente específico")
            else:
                print(f"   ❌ Nenhuma mensagem retornada")
                
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
    
    print(f"\n📊 Resultado: {success_count}/{len(agents_to_test)} agentes com mensagens específicas")
    return success_count == len(agents_to_test)

if __name__ == "__main__":
    print("🛡️ TESTE DAS MENSAGENS EDUCATIVEAS DOS GUARDRAILS")
    print("=" * 80)
    
    test1_success = test_educational_messages()
    test2_success = test_agent_specific_messages()
    
    print("\n" + "=" * 80)
    print("📋 RESUMO DO TESTE")
    print("=" * 80)
    
    if test1_success and test2_success:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("✅ Guardrails retornam mensagens educativas")
        print("✅ Mensagens são específicas por agente")
        print("✅ Usuário recebe orientações claras")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("🔧 Verificar implementação das mensagens educativas")
    
    print("=" * 80)
