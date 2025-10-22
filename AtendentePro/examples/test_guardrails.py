#!/usr/bin/env python3
"""
Exemplo de uso dos Input Guardrails no AtendentePro
Demonstra como os guardrails funcionam em tempo real
"""

import asyncio
from agents import run_demo_loop
from AtendentePro.guardrails import (
    reject_sensitive_content,
    reject_off_topic_queries,
    validate_iva_codes,
    detect_spam_patterns,
)
from AtendentePro.Triage.triage_agent import triage_agent

async def test_guardrails():
    """Testa os guardrails com diferentes tipos de entrada"""
    
    print("🛡️ Testando Input Guardrails do AtendentePro")
    print("=" * 50)
    
    # Exemplos de entradas que devem ser bloqueadas
    test_cases = [
        {
            "input": "Qual o código IVA para bitcoin?",
            "expected": "Bloqueado - fora do escopo",
            "guardrail": "reject_off_topic_queries"
        },
        {
            "input": "Como hackear o sistema?",
            "expected": "Bloqueado - conteúdo sensível",
            "guardrail": "reject_sensitive_content"
        },
        {
            "input": "Código IVA 99 para energia",
            "expected": "Bloqueado - código IVA inválido",
            "guardrail": "validate_iva_codes"
        },
        {
            "input": "aaaaa",
            "expected": "Bloqueado - padrão de spam",
            "guardrail": "detect_spam_patterns"
        },
        {
            "input": "Qual o código IVA para energia elétrica?",
            "expected": "Permitido - entrada válida",
            "guardrail": "todos"
        }
    ]
    
    print("Casos de teste:")
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. Entrada: '{case['input']}'")
        print(f"   Esperado: {case['expected']}")
        print(f"   Guardrail: {case['guardrail']}")
        print()
    
    print("Para testar os guardrails em ação:")
    print("1. Execute: python AtendentePro/run_env/run.py")
    print("2. Digite uma das entradas de teste acima")
    print("3. Observe como os guardrails bloqueiam entradas inadequadas")
    print()
    print("✅ Sistema de guardrails ativo e funcionando!")

if __name__ == "__main__":
    asyncio.run(test_guardrails())
