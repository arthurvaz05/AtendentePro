#!/usr/bin/env python3
"""
Teste da nova funcionalidade de guardrails específicos por agente
Testa se cada agente tem seus próprios temas permitidos baseados nos prompts
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
    get_agent_on_topic_keywords,
    reject_off_topic_queries_factory,
    get_guardrails_for_agent
)

def test_agent_specific_topics():
    """Testa se cada agente tem seus temas específicos"""
    
    print("🧪 TESTE: Temas Específicos por Agente")
    print("=" * 60)
    
    agents_to_test = [
        "Triage Agent",
        "Flow Agent", 
        "Interview Agent",
        "Answer Agent",
        "Confirmation Agent",
        "Knowledge Agent",
        "Usage Agent"
    ]
    
    for agent_name in agents_to_test:
        print(f"\n📋 {agent_name}")
        print("-" * 40)
        
        # Obter temas específicos do agente
        topics = get_agent_on_topic_keywords(agent_name)
        
        if topics:
            print(f"✅ Temas encontrados: {len(topics)}")
            print(f"📝 Primeiros 10 temas: {topics[:10]}")
            
            # Verificar temas específicos por agente
            if agent_name == "Confirmation Agent":
                confirmation_keywords = ["confirmar", "validação", "conferência"]
                found_confirmation = any(kw in topics for kw in confirmation_keywords)
                print(f"✅ Temas de confirmação encontrados: {found_confirmation}")
            
            elif agent_name == "Knowledge Agent":
                knowledge_keywords = ["procedimento", "documentação", "norma"]
                found_knowledge = any(kw in topics for kw in knowledge_keywords)
                print(f"✅ Temas de conhecimento encontrados: {found_knowledge}")
            
            elif agent_name == "Usage Agent":
                usage_keywords = ["usar o sistema", "como funciona", "ajuda plataforma"]
                found_usage = any(kw in topics for kw in usage_keywords)
                print(f"✅ Temas de uso encontrados: {found_usage}")
            
            elif agent_name == "Flow Agent":
                flow_keywords = ["duvida iva", "qual iva"]
                found_flow = any(kw in topics for kw in flow_keywords)
                print(f"✅ Temas específicos do Flow encontrados: {found_flow}")
        else:
            print("❌ Nenhum tema configurado para este agente")

def get_agent_test_cases(agent_name):
    """Retorna casos de teste específicos para cada agente"""
    
    base_cases = [
        {
            "query": "quem descobriu o brasil?",
            "expected": "bloqueado",
            "reason": "Tema fora do escopo"
        }
    ]
    
    if agent_name == "Triage Agent":
        return base_cases + [
            {
                "query": "Qual o código IVA para energia elétrica?",
                "expected": "permitido",
                "reason": "Tema relacionado a IVA"
            },
            {
                "query": "Como usar o sistema?",
                "expected": "permitido", 
                "reason": "Tema relacionado a uso do sistema"
            }
        ]
    
    elif agent_name == "Flow Agent":
        return base_cases + [
            {
                "query": "Qual o código IVA para industrialização?",
                "expected": "permitido",
                "reason": "Tema específico de IVA"
            },
            {
                "query": "Dúvida sobre IVA",
                "expected": "permitido",
                "reason": "Palavra-chave específica do Flow"
            }
        ]
    
    elif agent_name == "Confirmation Agent":
        return base_cases + [
            {
                "query": "Confirmar código F0",
                "expected": "permitido",
                "reason": "Tema de confirmação"
            },
            {
                "query": "Validação de código IVA",
                "expected": "permitido",
                "reason": "Tema de validação"
            }
        ]
    
    elif agent_name == "Knowledge Agent":
        return base_cases + [
            {
                "query": "Qual o procedimento para carta de correção?",
                "expected": "permitido",
                "reason": "Tema de procedimento"
            },
            {
                "query": "Documentação sobre NF-e",
                "expected": "permitido",
                "reason": "Tema de documentação"
            }
        ]
    
    elif agent_name == "Usage Agent":
        return base_cases + [
            {
                "query": "Como usar o sistema?",
                "expected": "permitido",
                "reason": "Tema de uso do sistema"
            },
            {
                "query": "Ajuda com a plataforma",
                "expected": "permitido",
                "reason": "Tema de ajuda"
            }
        ]
    
    else:  # Interview Agent, Answer Agent
        return base_cases + [
            {
                "query": "Qual o código IVA para energia elétrica?",
                "expected": "permitido",
                "reason": "Tema relacionado a IVA"
            }
        ]

def test_guardrail_factory():
    """Testa se o factory de guardrails está funcionando"""
    
    print("\n🧪 TESTE: Factory de Guardrails")
    print("=" * 60)
    
    agents_to_test = ["Triage Agent", "Flow Agent", "Confirmation Agent"]
    
    for agent_name in agents_to_test:
        print(f"\n📋 {agent_name}")
        print("-" * 40)
        
        # Obter guardrails para o agente
        guardrails = get_guardrails_for_agent(agent_name)
        
        print(f"✅ Guardrails encontrados: {len(guardrails)}")
        for i, guardrail in enumerate(guardrails):
            guardrail_name = getattr(guardrail, '__name__', str(type(guardrail).__name__))
            print(f"   {i+1}. {guardrail_name}")
        
        # Verificar se há guardrail específico de tópicos
        has_topic_guardrail = any(
            hasattr(g, '__name__') and 'reject_off_topic_queries' in g.__name__
            for g in guardrails
        )
        
        if has_topic_guardrail:
            print("✅ Guardrail de tópicos específico encontrado")
        else:
            print("❌ Guardrail de tópicos específico não encontrado")

if __name__ == "__main__":
    print("🛡️ TESTE DOS GUARDRAILS ESPECÍFICOS POR AGENTE")
    print("=" * 80)
    
    test_agent_specific_topics()
    test_guardrail_factory()
    
    print("\n" + "=" * 80)
    print("📋 RESUMO DO TESTE")
    print("=" * 80)
    print("✅ Cada agente deve ter seus próprios temas permitidos")
    print("✅ Guardrails específicos devem ser criados por factory")
    print("✅ Temas devem ser baseados nos prompts de cada agente")
    print("=" * 80)
