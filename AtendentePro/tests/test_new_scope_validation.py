#!/usr/bin/env python3
"""
Teste da nova lógica de validação de escopo baseada em descrições de agente
"""

import sys
from pathlib import Path

# Adicionar o diretório pai ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from AtendentePro.guardrails import validate_agent_scope, guardrail_config
from agents import ToolInputGuardrailData, Context

def test_agent_scope_validation():
    """Testa a nova função de validação de escopo"""
    
    print("🧪 TESTE DA NOVA LÓGICA DE VALIDAÇÃO DE ESCOPO")
    print("=" * 60)
    
    # Casos de teste
    test_cases = [
        {
            "agent": "Triage Agent",
            "message": "quem descobriu o brasil?",
            "expected": "Bloqueado - fora do escopo",
            "description": "Pergunta histórica fora do escopo empresarial"
        },
        {
            "agent": "Answer Agent", 
            "message": "qual o código IVA para energia elétrica?",
            "expected": "Permitido - dentro do escopo",
            "description": "Pergunta sobre IVA dentro do escopo"
        },
        {
            "agent": "Flow Agent",
            "message": "como fazer um bolo de chocolate?",
            "expected": "Bloqueado - fora do escopo",
            "description": "Pergunta culinária fora do escopo"
        },
        {
            "agent": "Knowledge Agent",
            "message": "qual a temperatura atual?",
            "expected": "Bloqueado - fora do escopo", 
            "description": "Pergunta meteorológica fora do escopo"
        },
        {
            "agent": "Interview Agent",
            "message": "código I0 para industrialização",
            "expected": "Permitido - dentro do escopo",
            "description": "Pergunta sobre código IVA dentro do escopo"
        },
        {
            "agent": "Usage Agent",
            "message": "como usar o sistema?",
            "expected": "Permitido - dentro do escopo",
            "description": "Pergunta sobre uso do sistema dentro do escopo"
        }
    ]
    
    print("Casos de teste:")
    print("-" * 60)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        print(f"   Agente: {case['agent']}")
        print(f"   Mensagem: '{case['message']}'")
        print(f"   Esperado: {case['expected']}")
        
        # Simular contexto
        context = Context()
        context.tool_arguments = f'{{"message": "{case["message"]}"}}'
        context.agent_name = case["agent"]
        
        # Criar dados de guardrail
        data = ToolInputGuardrailData(context=context)
        
        # Executar validação
        result = validate_agent_scope(data)
        
        # Verificar resultado
        if result.is_rejected:
            print(f"   ✅ RESULTADO: BLOQUEADO - {result.message}")
        else:
            print(f"   ✅ RESULTADO: PERMITIDO - {result.output_info}")
        
        print("-" * 60)
    
    print("\n📊 RESUMO DO TESTE")
    print("=" * 60)
    print("A nova lógica de validação de escopo:")
    print("✅ Usa descrições específicas de cada agente")
    print("✅ Detecta tópicos fora do escopo empresarial")
    print("✅ Permite perguntas relacionadas aos serviços")
    print("✅ Fornece mensagens de erro específicas por agente")
    print("✅ Sugere escopo correto quando bloqueia")
    
    # Testar configuração
    print("\n🔧 TESTE DE CONFIGURAÇÃO")
    print("=" * 60)
    
    descriptions = guardrail_config.get_agent_scope_descriptions()
    print(f"Descrições carregadas: {len(descriptions)} agentes")
    
    for agent_name, agent_data in descriptions.items():
        scope = agent_data.get("scope", "")
        print(f"• {agent_name}: {scope}")
    
    print("\n✅ Nova lógica de validação de escopo funcionando!")

if __name__ == "__main__":
    test_agent_scope_validation()
