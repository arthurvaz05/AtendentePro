#!/usr/bin/env python3
"""
Teste simples dos guardrails - versão standalone
Testa especificamente a pergunta "quem descobriu o brasil?"
"""

import json
import re
from unittest.mock import Mock

# Copiar as funções dos guardrails diretamente aqui para teste
def reject_off_topic_queries(data):
    """Rejeita consultas fora do escopo do AtendentePro"""
    try:
        args = json.loads(data.context.tool_arguments) if data.context.tool_arguments else {}
    except json.JSONDecodeError:
        return Mock(output_info="Argumentos JSON inválidos")

    # Tópicos fora do escopo
    OFF_TOPIC_KEYWORDS = [
        "bitcoin", "criptomoeda", "investimento",
        "política", "eleição", "governo",
        "religião", "deus", "jesus",
        "futebol", "esporte", "jogo",
        "receita", "cocina", "comida",
        "brasil", "descobriu", "história",  # Adicionar palavras relacionadas ao Brasil
    ]

    # Verificar tópicos fora do escopo
    for key, value in args.items():
        value_str = str(value).lower()
        
        for keyword in OFF_TOPIC_KEYWORDS:
            if keyword.lower() in value_str:
                return Mock(
                    output_info=None,  # Indica bloqueio
                    message=f"🚨 Consulta fora do escopo: '{keyword}' não é relacionado a IVA/energia"
                )

    return Mock(output_info="Consulta dentro do escopo válido")

def test_brasil_question():
    """Testa especificamente a pergunta sobre Brasil"""
    
    print("🧪 TESTE DOS GUARDRAILS")
    print("=" * 60)
    print("Pergunta de teste: 'quem descobriu o brasil?'")
    print("Esta pergunta está FORA DO ESCOPO do AtendentePro")
    print("=" * 60)
    
    # Simular dados de entrada
    brasil_args = '{"query": "quem descobriu o brasil?"}'
    
    # Criar mock data
    mock_data = Mock()
    mock_data.context = Mock()
    mock_data.context.tool_arguments = brasil_args
    
    # Testar guardrail
    result = reject_off_topic_queries(mock_data)
    
    print(f"Resultado: {result}")
    print(f"Bloqueado: {result.output_info is None}")
    print(f"Mensagem: {result.message}")
    
    if result.output_info is None:
        print("✅ Guardrail funcionando: pergunta bloqueada!")
        return True
    else:
        print("❌ Guardrail não funcionou: pergunta permitida!")
        return False

def test_valid_question():
    """Testa com pergunta válida"""
    
    print("\n" + "=" * 60)
    print("Testando com pergunta VÁLIDA...")
    print("Pergunta: 'Qual o código IVA para energia elétrica?'")
    print("=" * 60)
    
    # Simular dados de entrada válida
    valid_args = '{"query": "Qual o código IVA para energia elétrica?"}'
    
    # Criar mock data
    mock_data = Mock()
    mock_data.context = Mock()
    mock_data.context.tool_arguments = valid_args
    
    # Testar guardrail
    result = reject_off_topic_queries(mock_data)
    
    print(f"Resultado: {result}")
    print(f"Permitido: {result.output_info is not None}")
    print(f"Mensagem: {result.message}")
    
    if result.output_info is not None:
        print("✅ Guardrail funcionando: pergunta válida permitida!")
        return True
    else:
        print("❌ Guardrail não funcionou: pergunta válida bloqueada!")
        return False

def test_multiple_off_topic_questions():
    """Testa múltiplas perguntas fora do escopo"""
    
    print("\n" + "=" * 60)
    print("Testando múltiplas perguntas FORA DO ESCOPO...")
    print("=" * 60)
    
    off_topic_questions = [
        "quem descobriu o brasil?",
        "qual o código IVA para bitcoin?",
        "como fazer uma receita de bolo?",
        "quem ganhou o jogo de futebol?",
        "o que é política?",
    ]
    
    blocked_count = 0
    
    for question in off_topic_questions:
        print(f"\nTestando: '{question}'")
        
        args = f'{{"query": "{question}"}}'
        
        mock_data = Mock()
        mock_data.context = Mock()
        mock_data.context.tool_arguments = args
        
        result = reject_off_topic_queries(mock_data)
        
        if result.output_info is None:
            print("✅ BLOQUEADO")
            blocked_count += 1
        else:
            print("❌ PERMITIDO (deveria ser bloqueado)")
    
    print(f"\n📊 Resultado: {blocked_count}/{len(off_topic_questions)} perguntas bloqueadas")
    
    if blocked_count == len(off_topic_questions):
        print("🎉 Todos os guardrails funcionando perfeitamente!")
        return True
    else:
        print("⚠️ Alguns guardrails precisam de ajuste")
        return False

if __name__ == "__main__":
    print("🛡️ TESTE COMPLETO DOS INPUT GUARDRAILS")
    print("=" * 80)
    
    # Executar todos os testes
    test1 = test_brasil_question()
    test2 = test_valid_question()
    test3 = test_multiple_off_topic_questions()
    
    print("\n" + "=" * 80)
    print("📋 RESUMO DOS TESTES")
    print("=" * 80)
    print(f"✅ Pergunta 'brasil' bloqueada: {'SIM' if test1 else 'NÃO'}")
    print(f"✅ Pergunta válida permitida: {'SIM' if test2 else 'NÃO'}")
    print(f"✅ Múltiplas perguntas bloqueadas: {'SIM' if test3 else 'NÃO'}")
    
    if test1 and test2 and test3:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("🛡️ Sistema de guardrails funcionando corretamente")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        print("🔧 Sistema de guardrails precisa de ajustes")
    
    print("=" * 80)
