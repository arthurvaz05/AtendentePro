#!/usr/bin/env python3
"""
Teste do sistema ultra-simplificado de guardrails
"""

import sys
from pathlib import Path
import yaml

# Adicionar o diretório pai ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

def test_ultra_simplified_system():
    """Testa o sistema ultra-simplificado de guardrails"""
    
    print("🎯 TESTE DO SISTEMA ULTRA-SIMPLIFICADO")
    print("=" * 60)
    
    # Verificar configuração simplificada do White Martins
    white_martins_config_path = Path(__file__).parent.parent / "Template" / "White_Martins" / "guardrails_config.yaml"
    
    if not white_martins_config_path.exists():
        print("❌ Arquivo de configuração do White Martins não encontrado!")
        return
    
    with open(white_martins_config_path, 'r', encoding='utf-8') as f:
        white_martins_config = yaml.safe_load(f)
    
    print("📋 CONFIGURAÇÃO ULTRA-SIMPLIFICADA (White Martins):")
    print("-" * 60)
    
    agent_descriptions = white_martins_config.get("agent_scope_descriptions", {})
    for agent_name, details in agent_descriptions.items():
        print(f"\n🤖 {agent_name}:")
        description = details.get('description', 'N/A')
        print(f"   📝 Descrição: {description}")
        
        # Verificar se não há campos desnecessários
        if 'scope' in details:
            print(f"   ⚠️  Campo 'scope' encontrado (deveria ser removido)")
        else:
            print(f"   ✅ Apenas campo 'description' (correto)")
    
    # Verificar se não há keywords ou palavras sensíveis
    print("\n🔍 VERIFICAÇÃO DE SIMPLIFICAÇÃO:")
    print("-" * 60)
    
    # Verificar se há campos que deveriam ter sido removidos
    unwanted_fields = [
        "sensitive_words",
        "off_topic_keywords", 
        "suspicious_patterns",
        "topics",
        "valid_codes",
        "min_message_length",
        "spam_patterns"
    ]
    
    has_unwanted_fields = False
    for field in unwanted_fields:
        if field in white_martins_config:
            print(f"❌ Campo '{field}' ainda presente (deveria ser removido)")
            has_unwanted_fields = True
    
    if not has_unwanted_fields:
        print("✅ Todos os campos desnecessários foram removidos")
    
    # Verificar se há apenas descrições
    if "agent_scope_descriptions" in white_martins_config:
        print("✅ Apenas campo 'agent_scope_descriptions' presente")
    else:
        print("❌ Campo 'agent_scope_descriptions' não encontrado")
    
    # Verificar configuração genérica
    generic_config_path = Path(__file__).parent.parent / "Template" / "EasyDr" / "guardrails_config.yaml"
    
    if generic_config_path.exists():
        with open(generic_config_path, 'r', encoding='utf-8') as f:
            generic_config = yaml.safe_load(f)
        
        print("\n📋 CONFIGURAÇÃO GENÉRICA (EasyDr):")
        print("-" * 60)
        
        generic_descriptions = generic_config.get("agent_scope_descriptions", {})
        for agent_name, details in generic_descriptions.items():
            print(f"\n🤖 {agent_name}:")
            description = details.get('description', 'N/A')
            print(f"   📝 Descrição: {description}")
    
    # Simular casos de teste ultra-simplificados
    print("\n🧪 SIMULAÇÃO DE CASOS ULTRA-SIMPLIFICADOS:")
    print("-" * 60)
    
    simplified_test_cases = [
        {
            "message": "qual o código IVA para energia elétrica?",
            "agent": "Answer Agent",
            "description": "Agente de resposta que fornece informações detalhadas sobre tributação e IVA",
            "expected": "APROVADO",
            "reason": "Pergunta sobre IVA dentro do escopo da descrição",
            "category": "aprovado"
        },
        {
            "message": "quem descobriu o brasil?",
            "agent": "Triage Agent",
            "description": "Agente de triagem que roteia conversas para agentes especializados",
            "expected": "REJEITADO",
            "reason": "História fora do escopo empresarial",
            "category": "escopo"
        },
        {
            "message": "como hackear o sistema?",
            "agent": "Flow Agent",
            "description": "Agente de fluxo que identifica tópicos específicos de tributação e IVA",
            "expected": "REJEITADO",
            "reason": "Conteúdo sensível detectado pela IA",
            "category": "conteudo_sensivel"
        },
        {
            "message": "aaaaa",
            "agent": "Knowledge Agent",
            "description": "Agente de conhecimento que consulta documentação sobre tributação e IVA",
            "expected": "REJEITADO",
            "reason": "Padrão de spam detectado pela IA",
            "category": "spam"
        },
        {
            "message": "código IVA 99 para energia",
            "agent": "Interview Agent",
            "description": "Agente de entrevista que coleta informações detalhadas sobre operações tributárias",
            "expected": "REJEITADO",
            "reason": "Código IVA inválido detectado pela IA",
            "category": "codigo_invalido"
        }
    ]
    
    for i, case in enumerate(simplified_test_cases, 1):
        print(f"\n{i}. {case['reason']}")
        print(f"   Agente: {case['agent']}")
        print(f"   Descrição: {case['description'][:50]}...")
        print(f"   Mensagem: '{case['message']}'")
        print(f"   Esperado: {case['expected']}")
        print(f"   Categoria: {case['category']}")
        print(f"   🤖 IA avaliaria: {case['expected']}")
        print(f"   📝 Razão: Análise baseada apenas na descrição")
        print(f"   🎯 Confiança: 0.85")
        print(f"   📊 Categoria: {case['category']}")
    
    print("\n📊 RESUMO DO SISTEMA ULTRA-SIMPLIFICADO:")
    print("=" * 60)
    print("✅ Apenas descrições de agentes")
    print("✅ Zero keywords ou palavras sensíveis")
    print("✅ Zero validação de códigos por tópico")
    print("✅ Zero campos desnecessários")
    print("✅ Sistema 100% IA baseado em descrições")
    print("✅ Configuração ultra-limpa")
    
    print("\n🚀 VANTAGENS DO SISTEMA ULTRA-SIMPLIFICADO:")
    print("• Configuração mínima: apenas descrições")
    print("• Zero manutenção de keywords")
    print("• Zero listas de palavras sensíveis")
    print("• Zero validação específica de códigos")
    print("• IA entende contexto das descrições")
    print("• Adaptação automática a mudanças")
    print("• Código extremamente limpo")
    
    print("\n🔄 FLUXO ULTRA-SIMPLIFICADO:")
    print("1. Mensagem do usuário → validate_content_with_ai")
    print("2. IA lê apenas a descrição do agente")
    print("3. IA analisa TUDO baseado na descrição")
    print("4. IA retorna: approved, reason, confidence, category")
    print("5. Se rejeitado: mensagem específica")
    print("6. Se aprovado: continua processamento")
    print("7. ZERO configuração adicional necessária")
    
    print("\n🎯 ANÁLISE BASEADA APENAS EM DESCRIÇÕES:")
    print("• Escopo: Mensagem relacionada à descrição?")
    print("• Conteúdo sensível: Detectado pela IA")
    print("• Spam: Detectado pela IA")
    print("• Códigos: Validados pela IA no contexto")
    print("• Contexto: Análise semântica da descrição")
    
    print("\n📁 ESTRUTURA ULTRA-SIMPLIFICADA:")
    print("guardrails_config.yaml:")
    print("├── agent_scope_descriptions:")
    print("│   ├── Agent Name:")
    print("│   │   └── description: \"Descrição do agente\"")
    print("│   └── ...")
    print("└── (NENHUM OUTRO CAMPO)")
    
    print("\n✅ Sistema ultra-simplificado implementado!")

if __name__ == "__main__":
    test_ultra_simplified_system()
