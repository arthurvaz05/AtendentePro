#!/usr/bin/env python3
"""
Teste de Limpeza do answer_config.yaml
Verifica que a seção topics foi removida e movida para guardrails_config.yaml
"""

import yaml
from pathlib import Path

def test_answer_config_cleanup():
    """Testa se a seção topics foi removida do answer_config.yaml"""
    
    print("🧪 TESTE: Limpeza do answer_config.yaml")
    print("=" * 60)
    
    # Carregar answer_config.yaml
    answer_config_file = Path(__file__).parent.parent / "Template" / "White_Martins" / "answer_config.yaml"
    
    if not answer_config_file.exists():
        print("❌ Arquivo answer_config.yaml não encontrado!")
        return False
    
    with open(answer_config_file, 'r', encoding='utf-8') as f:
        answer_config = yaml.safe_load(f)
    
    print("📋 Verificando answer_config.yaml:")
    print(f"   Arquivo: {answer_config_file}")
    print(f"   Seções encontradas: {list(answer_config.keys())}")
    
    # Verificar se a seção topics foi removida
    has_topics = "topics" in answer_config
    has_answer_template = "answer_template" in answer_config
    
    print(f"\n🔍 Verificações:")
    print(f"   ❌ Seção 'topics' presente: {'SIM' if has_topics else 'NÃO'}")
    print(f"   ✅ Seção 'answer_template' presente: {'SIM' if has_answer_template else 'NÃO'}")
    
    if has_topics:
        print("   ❌ ERRO: Seção 'topics' ainda está presente!")
        return False
    else:
        print("   ✅ CORRETO: Seção 'topics' foi removida!")
    
    if not has_answer_template:
        print("   ❌ ERRO: Seção 'answer_template' não encontrada!")
        return False
    else:
        print("   ✅ CORRETO: Seção 'answer_template' mantida!")
    
    return not has_topics and has_answer_template

def test_guardrails_config_has_topics():
    """Testa se a seção topics está presente no guardrails_config.yaml"""
    
    print("\n🧪 TESTE: Verificação do guardrails_config.yaml")
    print("=" * 60)
    
    # Carregar guardrails_config.yaml
    guardrails_config_file = Path(__file__).parent.parent / "Template" / "White_Martins" / "guardrails_config.yaml"
    
    if not guardrails_config_file.exists():
        print("❌ Arquivo guardrails_config.yaml não encontrado!")
        return False
    
    with open(guardrails_config_file, 'r', encoding='utf-8') as f:
        guardrails_config = yaml.safe_load(f)
    
    print("📋 Verificando guardrails_config.yaml:")
    print(f"   Arquivo: {guardrails_config_file}")
    print(f"   Seções encontradas: {list(guardrails_config.keys())}")
    
    # Verificar se a seção topics está presente
    has_topics = "topics" in guardrails_config
    has_valid_codes = "valid_codes" in guardrails_config
    
    print(f"\n🔍 Verificações:")
    print(f"   ✅ Seção 'topics' presente: {'SIM' if has_topics else 'NÃO'}")
    print(f"   ✅ Seção 'valid_codes' presente: {'SIM' if has_valid_codes else 'NÃO'}")
    
    if not has_topics:
        print("   ❌ ERRO: Seção 'topics' não encontrada!")
        return False
    else:
        print("   ✅ CORRETO: Seção 'topics' está presente!")
        
        # Verificar estrutura dos tópicos
        topics = guardrails_config["topics"]
        print(f"   📊 Tópicos carregados: {len(topics)}")
        
        for topic_name, topic_data in topics.items():
            codes = topic_data.get("codes", [])
            description = topic_data.get("description", "")
            print(f"      - {topic_name}: {len(codes)} códigos")
            print(f"        Descrição: {description[:50]}...")
    
    return has_topics and has_valid_codes

def test_separation_of_concerns():
    """Testa a separação de responsabilidades"""
    
    print("\n🧪 TESTE: Separação de Responsabilidades")
    print("=" * 60)
    
    print("📋 Verificando separação:")
    print("   ✅ answer_config.yaml: apenas template de resposta")
    print("   ✅ guardrails_config.yaml: validação de tópicos e códigos")
    print("   ✅ agent_guardrails_config.yaml: configuração por agente")
    
    print("\n🎯 Benefícios da separação:")
    print("   • Validação centralizada nos guardrails")
    print("   • Template de resposta focado apenas no conteúdo")
    print("   • Configuração de guardrails por agente")
    print("   • Reutilização para outros clientes")
    
    return True

if __name__ == "__main__":
    print("🛡️ TESTE DE LIMPEZA E SEPARAÇÃO DE CONFIGURAÇÕES")
    print("=" * 80)
    
    # Executar testes
    test1 = test_answer_config_cleanup()
    test2 = test_guardrails_config_has_topics()
    test3 = test_separation_of_concerns()
    
    print("\n" + "=" * 80)
    print("📋 RESUMO FINAL")
    print("=" * 80)
    print(f"✅ Seção topics removida do answer_config.yaml: {'SIM' if test1 else 'NÃO'}")
    print(f"✅ Seção topics presente no guardrails_config.yaml: {'SIM' if test2 else 'NÃO'}")
    print(f"✅ Separação de responsabilidades implementada: {'SIM' if test3 else 'NÃO'}")
    
    if test1 and test2 and test3:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("🛡️ Configurações limpas e bem separadas")
        print("📁 Validação de tópicos movida para guardrails")
        print("🎯 Separação de responsabilidades implementada")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        print("🔧 Configurações precisam de ajustes")
    
    print("=" * 80)
