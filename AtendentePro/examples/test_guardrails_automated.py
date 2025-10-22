#!/usr/bin/env python3
"""
Teste automatizado dos Input Guardrails
Testa a pergunta "quem descobriu o brasil?" com todos os agentes
"""

import asyncio
import sys
from pathlib import Path

# Adicionar o diretório pai ao path
sys.path.append(str(Path(__file__).parent.parent))

from AtendentePro.agent_network import configure_agent_network
from AtendentePro.Triage.triage_agent import triage_agent
from AtendentePro.Flow.flow_agent import flow_agent
from AtendentePro.Interview.interview_agent import interview_agent
from AtendentePro.Answer.answer_agent import answer_agent
from AtendentePro.Confirmation.confirmation_agent import confirmation_agent
from AtendentePro.Knowledge.knowledge_agent import knowledge_agent
from AtendentePro.Usage.usage_agent import usage_agent

async def test_agent_with_question(agent, agent_name, question):
    """Testa um agente específico com uma pergunta"""
    print(f"\n🧪 Testando {agent_name}")
    print(f"Pergunta: '{question}'")
    print("-" * 50)
    
    try:
        # Simular uma mensagem do usuário
        from agents import UserMessage
        message = UserMessage(content=question)
        
        # Executar o agente
        result = await agent.run(message)
        
        print(f"✅ {agent_name} executou sem bloqueio")
        print(f"Resposta: {result.content[:100]}...")
        
    except Exception as e:
        print(f"🚨 {agent_name} bloqueou a pergunta!")
        print(f"Erro: {str(e)}")
    
    print("=" * 50)

async def test_all_agents():
    """Testa todos os agentes com a pergunta fora do escopo"""
    
    # Configurar a rede de agentes
    configure_agent_network()
    
    # Pergunta que deve ser bloqueada
    question = "quem descobriu o brasil?"
    
    print("🛡️ TESTE DOS INPUT GUARDRAILS")
    print("=" * 60)
    print(f"Pergunta de teste: '{question}'")
    print("Esta pergunta está FORA DO ESCOPO do AtendentePro")
    print("(deveria ser bloqueada pelos guardrails)")
    print("=" * 60)
    
    # Lista de agentes para testar
    agents_to_test = [
        (triage_agent, "Triage Agent"),
        (flow_agent, "Flow Agent"),
        (interview_agent, "Interview Agent"),
        (answer_agent, "Answer Agent"),
        (confirmation_agent, "Confirmation Agent"),
        (knowledge_agent, "Knowledge Agent"),
        (usage_agent, "Usage Agent"),
    ]
    
    # Testar cada agente
    for agent, name in agents_to_test:
        await test_agent_with_question(agent, name, question)
    
    print("\n📊 RESUMO DO TESTE")
    print("=" * 60)
    print("Se os guardrails estão funcionando:")
    print("- Perguntas fora do escopo devem ser BLOQUEADAS")
    print("- Agentes devem retornar erro ou mensagem de bloqueio")
    print("- Sistema deve proteger contra consultas inadequadas")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_all_agents())
