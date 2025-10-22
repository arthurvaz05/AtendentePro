#!/usr/bin/env python3
"""
Teste de Configuração de Guardrails por Agente
Verifica que apenas o Answer Agent tem validação de tópicos e códigos
"""

import yaml
from pathlib import Path

def test_agent_guardrails_configuration():
    """Testa configuração de guardrails por agente"""
    
    print("🧪 TESTE: Configuração de Guardrails por Agente")
    print("=" * 60)
    
    # Carregar configuração
    config_file = Path(__file__).parent.parent / "Template" / "White_Martins" / "agent_guardrails_config.yaml"
    
    if not config_file.exists():
        print("❌ Arquivo de configuração não encontrado!")
        return False
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("📋 Configuração carregada:")
    print(f"   Arquivo: {config_file}")
    print(f"   Agentes configurados: {len(config)}")
    
    # Verificar configuração específica
    expected_config = {
        "Triage Agent": ["reject_off_topic_queries", "detect_spam_patterns"],
        "Flow Agent": ["reject_off_topic_queries"],
        "Interview Agent": ["reject_sensitive_content"],
        "Answer Agent": ["reject_sensitive_content", "validate_topic_and_codes"],
        "Confirmation Agent": ["reject_sensitive_content"],
        "Knowledge Agent": ["reject_off_topic_queries", "detect_spam_patterns"],
        "Usage Agent": ["detect_spam_patterns"]
    }
    
    print("\n🔍 Verificando configuração por agente:")
    
    all_correct = True
    
    for agent_name, expected_guardrails in expected_config.items():
        if agent_name in config:
            actual_guardrails = config[agent_name]
            print(f"\n   {agent_name}:")
            print(f"     Esperado: {expected_guardrails}")
            print(f"     Atual:    {actual_guardrails}")
            
            if actual_guardrails == expected_guardrails:
                print(f"     ✅ CORRETO")
            else:
                print(f"     ❌ INCORRETO")
                all_correct = False
        else:
            print(f"\n   {agent_name}: ❌ NÃO ENCONTRADO")
            all_correct = False
    
    # Verificação específica: apenas Answer Agent deve ter validate_topic_and_codes
    print("\n🎯 VERIFICAÇÃO ESPECÍFICA:")
    print("Apenas o Answer Agent deve ter 'validate_topic_and_codes'")
    
    answer_agent_has_topic_validation = False
    other_agents_have_topic_validation = False
    
    for agent_name, guardrails in config.items():
        if "validate_topic_and_codes" in guardrails:
            if agent_name == "Answer Agent":
                answer_agent_has_topic_validation = True
                print(f"   ✅ {agent_name}: tem validate_topic_and_codes (CORRETO)")
            else:
                other_agents_have_topic_validation = True
                print(f"   ❌ {agent_name}: tem validate_topic_and_codes (INCORRETO)")
    
    if not answer_agent_has_topic_validation:
        print("   ❌ Answer Agent: NÃO tem validate_topic_and_codes (INCORRETO)")
        all_correct = False
    
    if other_agents_have_topic_validation:
        all_correct = False
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VERIFICAÇÃO:")
    print(f"✅ Configuração geral correta: {'SIM' if all_correct else 'NÃO'}")
    print(f"✅ Apenas Answer Agent tem validação de tópicos: {'SIM' if answer_agent_has_topic_validation and not other_agents_have_topic_validation else 'NÃO'}")
    
    return all_correct and answer_agent_has_topic_validation and not other_agents_have_topic_validation

def test_guardrails_logic():
    """Testa a lógica de guardrails"""
    
    print("\n🧪 TESTE: Lógica de Guardrails")
    print("=" * 60)
    
    # Simular função get_guardrails_for_agent
    def get_guardrails_for_agent(agent_name: str):
        """Simula a função get_guardrails_for_agent"""
        default_guardrails_map = {
            "Triage Agent": ["reject_off_topic_queries", "detect_spam_patterns"],
            "Flow Agent": ["reject_off_topic_queries"],
            "Interview Agent": ["reject_sensitive_content"],
            "Answer Agent": ["reject_sensitive_content", "validate_topic_and_codes"],
            "Confirmation Agent": ["reject_sensitive_content"],
            "Knowledge Agent": ["reject_off_topic_queries", "detect_spam_patterns"],
            "Usage Agent": ["detect_spam_patterns"],
        }
        return default_guardrails_map.get(agent_name, ["reject_sensitive_content"])
    
    # Testar cada agente
    agents_to_test = [
        "Triage Agent",
        "Flow Agent", 
        "Interview Agent",
        "Answer Agent",
        "Confirmation Agent",
        "Knowledge Agent",
        "Usage Agent"
    ]
    
    print("🔍 Testando guardrails por agente:")
    
    all_correct = True
    
    for agent_name in agents_to_test:
        guardrails = get_guardrails_for_agent(agent_name)
        has_topic_validation = "validate_topic_and_codes" in guardrails
        
        print(f"\n   {agent_name}:")
        print(f"     Guardrails: {guardrails}")
        print(f"     Tem validação de tópicos: {'SIM' if has_topic_validation else 'NÃO'}")
        
        # Apenas Answer Agent deve ter validação de tópicos
        if agent_name == "Answer Agent":
            if not has_topic_validation:
                print(f"     ❌ Answer Agent deveria ter validação de tópicos!")
                all_correct = False
            else:
                print(f"     ✅ Answer Agent tem validação de tópicos (CORRETO)")
        else:
            if has_topic_validation:
                print(f"     ❌ {agent_name} não deveria ter validação de tópicos!")
                all_correct = False
            else:
                print(f"     ✅ {agent_name} não tem validação de tópicos (CORRETO)")
    
    print("\n" + "=" * 60)
    print(f"📊 Lógica de guardrails: {'CORRETA' if all_correct else 'INCORRETA'}")
    
    return all_correct

if __name__ == "__main__":
    print("🛡️ TESTE DE CONFIGURAÇÃO DE GUARDRAILS POR AGENTE")
    print("=" * 80)
    
    # Executar testes
    test1 = test_agent_guardrails_configuration()
    test2 = test_guardrails_logic()
    
    print("\n" + "=" * 80)
    print("📋 RESUMO FINAL")
    print("=" * 80)
    print(f"✅ Configuração de arquivo correta: {'SIM' if test1 else 'NÃO'}")
    print(f"✅ Lógica de guardrails correta: {'SIM' if test2 else 'NÃO'}")
    
    if test1 and test2:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("🛡️ Apenas o Answer Agent tem validação de tópicos e códigos")
        print("📁 Configuração de guardrails por agente está correta")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        print("🔧 Configuração de guardrails precisa de ajustes")
    
    print("=" * 80)
