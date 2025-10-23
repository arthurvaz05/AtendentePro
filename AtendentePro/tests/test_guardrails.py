"""
Teste do sistema de guardrails
"""

import asyncio
import sys
import os

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from guardrails import GuardrailSystem


async def test_guardrails():
    """Testa o sistema de guardrails"""
    print("🧪 Testando Sistema de Guardrails...")
    
    # Testa com configuração genérica
    print("\n1️⃣ Testando com configuração genérica:")
    generic_system = GuardrailSystem()
    
    # Testa com configuração específica da White Martins
    print("\n2️⃣ Testando com configuração White Martins:")
    white_martins_config = "Template/White_Martins/guardrails_config.yaml"
    wm_system = GuardrailSystem(white_martins_config)
    
    # Mensagens de teste
    test_cases = [
        {
            "message": "Preciso de uma válvula pneumática para minha aplicação",
            "agent": "triage_agent",
            "expected": True,
            "description": "Mensagem relevante para White Martins"
        },
        {
            "message": "Como resolver 2x + 5 = 11?",
            "agent": "triage_agent", 
            "expected": False,
            "description": "Matemática - fora do escopo"
        },
        {
            "message": "Quero informações sobre compressores",
            "agent": "answer_agent",
            "expected": True,
            "description": "Consulta sobre produto White Martins"
        },
        {
            "message": "Me ajude com programação Python",
            "agent": "knowledge_agent",
            "expected": False,
            "description": "Programação - fora do escopo"
        },
        {
            "message": "Qual é a especificação técnica do cilindro pneumático?",
            "agent": "answer_agent",
            "expected": True,
            "description": "Consulta técnica relevante"
        }
    ]
    
    print(f"\n📋 Executando {len(test_cases)} testes...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Teste {i}: {test_case['description']} ---")
        print(f"Mensagem: {test_case['message']}")
        print(f"Agente: {test_case['agent']}")
        
        try:
            result = await wm_system.evaluate_message(
                test_case['message'], 
                test_case['agent']
            )
            
            print(f"✅ Resultado:")
            print(f"   Escopo: {result.is_in_scope}")
            print(f"   Confiança: {result.confidence:.2f}")
            print(f"   Ação: {result.suggested_action}")
            print(f"   Razão: {result.reasoning}")
            
            # Verifica se o resultado está conforme esperado
            if result.is_in_scope == test_case['expected']:
                print(f"✅ Teste PASSOU - Resultado conforme esperado")
            else:
                print(f"❌ Teste FALHOU - Esperado: {test_case['expected']}, Obtido: {result.is_in_scope}")
                
        except Exception as e:
            print(f"❌ Erro no teste: {str(e)}")
    
    print(f"\n🎯 Teste concluído!")


async def test_configuration_loading():
    """Testa carregamento de configurações"""
    print("\n🔧 Testando carregamento de configurações...")
    
    try:
        # Testa configuração genérica
        generic_system = GuardrailSystem()
        print("✅ Configuração genérica carregada")
        
        # Testa configuração específica
        wm_system = GuardrailSystem("Template/White_Martins/guardrails_config.yaml")
        print("✅ Configuração White Martins carregada")
        
        # Verifica se tem configurações para diferentes agentes
        agents = ["triage_agent", "flow_agent", "interview_agent", "answer_agent"]
        for agent in agents:
            config = wm_system.config.get_agent_config(agent)
            if config:
                print(f"✅ Configuração encontrada para {agent}")
            else:
                print(f"❌ Configuração não encontrada para {agent}")
                
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {str(e)}")


if __name__ == "__main__":
    print("🚀 Iniciando testes do sistema de guardrails...")
    
    # Executa testes
    asyncio.run(test_configuration_loading())
    asyncio.run(test_guardrails())
    
    print("\n✨ Todos os testes concluídos!")

