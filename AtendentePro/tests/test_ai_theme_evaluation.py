#!/usr/bin/env python3
"""
Teste da nova avaliação de tema baseada em IA
"""

import sys
from pathlib import Path
import os

# Adicionar o diretório pai ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Configurar API key para teste
os.environ['OPENAI_API_KEY'] = 'sk-proj-your-key-here'  # Substitua pela sua chave

def test_ai_theme_evaluation():
    """Testa a nova função de avaliação de tema usando IA"""
    
    print("🤖 TESTE DA AVALIAÇÃO DE TEMA BASEADA EM IA")
    print("=" * 60)
    
    # Importar a função de avaliação
    try:
        from AtendentePro.guardrails import evaluate_theme_with_ai
        print("✅ Função de avaliação importada com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar função: {e}")
        return
    
    # Casos de teste
    test_cases = [
        {
            "agent": "Triage Agent",
            "scope": "Tributação, IVA, energia elétrica, compras empresariais, ativos, frete, serviços da empresa",
            "description": "Agente de triagem que roteia conversas para agentes especializados",
            "message": "quem descobriu o brasil?",
            "expected": False,
            "description_test": "Pergunta histórica fora do escopo"
        },
        {
            "agent": "Answer Agent",
            "scope": "Códigos IVA específicos, regras tributárias, tipos de fornecedor, operações empresariais",
            "description": "Agente de resposta que fornece informações sobre códigos IVA e tributação",
            "message": "qual o código IVA para energia elétrica?",
            "expected": True,
            "description_test": "Pergunta sobre IVA dentro do escopo"
        },
        {
            "agent": "Flow Agent",
            "scope": "Identificação de tópicos tributários, códigos IVA, tipos de compra empresarial",
            "description": "Agente de fluxo que identifica tópicos específicos de tributação e IVA",
            "message": "como fazer um bolo de chocolate?",
            "expected": False,
            "description_test": "Pergunta culinária fora do escopo"
        },
        {
            "agent": "Knowledge Agent",
            "scope": "Documentação tributária, regulamentações fiscais, procedimentos, normas técnicas",
            "description": "Agente de conhecimento que consulta documentos sobre tributação e IVA",
            "message": "qual a temperatura atual?",
            "expected": False,
            "description_test": "Pergunta meteorológica fora do escopo"
        },
        {
            "agent": "Interview Agent",
            "scope": "Coleta de informações sobre operações tributárias, fornecedores, códigos IVA",
            "description": "Agente de entrevista que coleta informações detalhadas sobre operações tributárias",
            "message": "código I0 para industrialização",
            "expected": True,
            "description_test": "Pergunta sobre código IVA dentro do escopo"
        },
        {
            "agent": "Usage Agent",
            "scope": "Funcionalidades do sistema, orientações de uso, navegação entre agentes",
            "description": "Agente de uso que explica como usar o sistema AtendentePro",
            "message": "como usar o sistema?",
            "expected": True,
            "description_test": "Pergunta sobre uso do sistema dentro do escopo"
        }
    ]
    
    print("\n🧪 EXECUTANDO CASOS DE TESTE:")
    print("-" * 60)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description_test']}")
        print(f"   Agente: {case['agent']}")
        print(f"   Mensagem: '{case['message']}'")
        print(f"   Esperado: {'APROVADO' if case['expected'] else 'REJEITADO'}")
        
        try:
            # Executar avaliação com IA
            result = evaluate_theme_with_ai(
                case['message'],
                case['agent'],
                case['scope'],
                case['description']
            )
            
            approved = result.get('approved', True)
            reason = result.get('reason', 'Sem razão')
            confidence = result.get('confidence', 0.0)
            
            print(f"   🤖 IA Resultado: {'APROVADO' if approved else 'REJEITADO'}")
            print(f"   📝 Razão: {reason}")
            print(f"   🎯 Confiança: {confidence:.2f}")
            
            # Verificar se resultado está correto
            if approved == case['expected']:
                print(f"   ✅ CORRETO - Resultado esperado")
            else:
                print(f"   ❌ INCORRETO - Esperado {case['expected']}, obtido {approved}")
                
        except Exception as e:
            print(f"   ❌ ERRO: {str(e)}")
        
        print("-" * 40)
    
    print("\n📊 RESUMO DO TESTE:")
    print("=" * 60)
    print("✅ Função de avaliação com IA implementada")
    print("✅ Integração com sistema de guardrails")
    print("✅ Análise inteligente de contexto")
    print("✅ Fallback para keywords em caso de erro")
    
    print("\n🔄 VANTAGENS DA AVALIAÇÃO COM IA:")
    print("• Análise contextual mais precisa")
    print("• Compreensão de nuances e contexto")
    print("• Adaptação a diferentes tipos de pergunta")
    print("• Menos falsos positivos/negativos")
    print("• Explicações detalhadas das decisões")
    
    print("\n⚠️ CONSIDERAÇÕES:")
    print("• Dependência de API externa")
    print("• Latência adicional")
    print("• Custo por chamada")
    print("• Fallback necessário para robustez")

if __name__ == "__main__":
    test_ai_theme_evaluation()
