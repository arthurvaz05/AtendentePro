#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento dos guardrails em todos os agentes
através do comando run.

Este script testa:
1. Perguntas dentro do escopo
2. Perguntas fora do escopo
3. Comportamento de handoff entre agentes
4. Respostas adequadas de cada agente
"""

import asyncio
import subprocess
import sys
import os
from typing import List, Dict, Any

class GuardrailsTester:
    """Classe para testar guardrails através do comando run"""
    
    def __init__(self):
        self.base_dir = "/Users/arthurvaz/Desktop/Monkai/AtendentePRO"
        self.agents = [
            "triage", "flow", "interview", "answer", 
            "confirmation", "knowledge", "usage"
        ]
        
        # Perguntas de teste
        self.test_questions = {
            "in_scope": [
                "Preciso de ajuda com código IVA para compra de equipamento",
                "Como classificar uma operação de industrialização?",
                "Qual o código IVA para serviços de frete?",
                "Como usar o sistema de atendimento?",
                "Preciso de informações sobre tributação brasileira"
            ],
            "out_of_scope": [
                "quem descobriu o brasil",
                "Como resolver a equação 2x + 5 = 11?",
                "Me ajude com programação Python",
                "Qual o melhor filme de 2024?",
                "Como fazer um bolo de chocolate?"
            ]
        }
    
    def run_agent_test(self, agent: str, question: str) -> Dict[str, Any]:
        """Executa teste de um agente com uma pergunta específica"""
        print(f"\n{'='*60}")
        print(f"TESTANDO {agent.upper()} AGENT")
        print(f"Pergunta: {question}")
        print(f"{'='*60}")
        
        try:
            # Comando para executar o agente
            cmd = [
                "bash", "-c", 
                f"cd {self.base_dir} && source venv/bin/activate && echo '{question}' | python -m AtendentePro.run_env.run {agent}"
            ]
            
            # Executar comando
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30,
                cwd=self.base_dir
            )
            
            # Determinar se foi sucesso baseado no comportamento esperado
            # InputGuardrailTripwireTriggered é sucesso para perguntas fora do escopo
            stderr_lower = result.stderr.lower()
            is_guardrail_tripwire = "inputguardrailtripwiretriggered" in stderr_lower
            
            # Determinar se é pergunta fora do escopo
            is_out_of_scope = any(phrase in question.lower() for phrase in [
                "descobriu o brasil", "equação", "python", "filme", "bolo"
            ])
            
            # Sucesso se:
            # 1. Return code 0 (execução normal)
            # 2. Guardrail tripwire para pergunta fora do escopo (comportamento correto)
            success = (result.returncode == 0) or (is_guardrail_tripwire and is_out_of_scope)
            
            return {
                "agent": agent,
                "question": question,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": success,
                "is_guardrail_tripwire": is_guardrail_tripwire,
                "is_out_of_scope": is_out_of_scope
            }
            
        except subprocess.TimeoutExpired:
            return {
                "agent": agent,
                "question": question,
                "return_code": -1,
                "stdout": "",
                "stderr": "Timeout - comando demorou mais de 30 segundos",
                "success": False
            }
        except Exception as e:
            return {
                "agent": agent,
                "question": question,
                "return_code": -1,
                "stdout": "",
                "stderr": f"Erro: {str(e)}",
                "success": False
            }
    
    def analyze_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa a resposta do agente para determinar se os guardrails funcionaram"""
        stdout = result["stdout"].lower()
        stderr = result["stderr"].lower()
        
        # Usar informações já calculadas
        is_out_of_scope = result.get("is_out_of_scope", False)
        is_guardrail_tripwire = result.get("is_guardrail_tripwire", False)
        
        # Indicadores de guardrails funcionando (respostas educativas)
        guardrail_indicators = [
            "fora do escopo",
            "não relacionado",
            "especializado em",
            "processos fiscais",
            "tributação brasileira",
            "códigos iva",
            "white martins",
            "desculpe, mas só posso",
            "sua pergunta não está relacionada"
        ]
        
        # Indicadores de resposta inadequada
        inappropriate_indicators = [
            "pedro álvares cabral",
            "descobrimento do brasil",
            "resolver a equação",
            "programação python",
            "filme de 2024",
            "bolo de chocolate"
        ]
        
        # Verificar se guardrails funcionaram
        guardrails_working = any(indicator in stdout for indicator in guardrail_indicators)
        inappropriate_response = any(indicator in stdout for indicator in inappropriate_indicators)
        
        # Comportamento correto:
        # 1. Para perguntas fora do escopo: guardrail tripwire OU resposta educativa
        # 2. Para perguntas dentro do escopo: resposta adequada sem tripwire
        if is_out_of_scope:
            correct_behavior = is_guardrail_tripwire or guardrails_working
            actual_behavior = "block" if (is_guardrail_tripwire or guardrails_working) else "allow"
        else:
            correct_behavior = not inappropriate_response and not is_guardrail_tripwire
            actual_behavior = "allow" if not inappropriate_response else "block"
        
        return {
            "guardrails_working": guardrails_working,
            "inappropriate_response": inappropriate_response,
            "is_out_of_scope": is_out_of_scope,
            "is_guardrail_tripwire": is_guardrail_tripwire,
            "expected_behavior": "block" if is_out_of_scope else "allow",
            "actual_behavior": actual_behavior,
            "correct_behavior": correct_behavior
        }
    
    def run_quick_test(self):
        """Executa teste rápido com apenas algumas perguntas"""
        print("⚡ TESTE RÁPIDO DE GUARDRAILS")
        print("="*50)
        
        # Testar apenas alguns agentes com perguntas críticas
        quick_tests = [
            ("answer", "quem descobriu o brasil"),
            ("usage", "quem descobriu o brasil"),
            ("triage", "quem descobriu o brasil"),
            ("answer", "Preciso de ajuda com código IVA"),
            ("usage", "Como usar o sistema?")
        ]
        
        results = []
        for agent, question in quick_tests:
            result = self.run_agent_test(agent, question)
            analysis = self.analyze_response(result)
            results.append({**result, **analysis})
        
        self.generate_report(results)
        return results
    
    def run_comprehensive_test(self):
        """Executa teste completo de todos os agentes"""
        print("🚀 INICIANDO TESTES COMPREHENSIVOS DE GUARDRAILS")
        print("="*80)
        
        results = []
        
        # Testar cada agente com perguntas dentro e fora do escopo
        for agent in self.agents:
            print(f"\n📋 TESTANDO AGENTE: {agent.upper()}")
            
            # Testar perguntas dentro do escopo
            for question in self.test_questions["in_scope"][:2]:  # Limitar para não demorar muito
                result = self.run_agent_test(agent, question)
                analysis = self.analyze_response(result)
                results.append({**result, **analysis})
            
            # Testar perguntas fora do escopo
            for question in self.test_questions["out_of_scope"][:2]:  # Limitar para não demorar muito
                result = self.run_agent_test(agent, question)
                analysis = self.analyze_response(result)
                results.append({**result, **analysis})
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]):
        """Gera relatório dos testes"""
        print("\n" + "="*80)
        print("📊 RELATÓRIO DE TESTES DE GUARDRAILS")
        print("="*80)
        
        # Estatísticas gerais
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r["success"])
        correct_behavior = sum(1 for r in results if r["correct_behavior"])
        
        print(f"\n📈 ESTATÍSTICAS GERAIS:")
        print(f"   Total de testes: {total_tests}")
        print(f"   Testes executados com sucesso: {successful_tests}")
        print(f"   Comportamento correto: {correct_behavior}")
        print(f"   Taxa de sucesso: {(successful_tests/total_tests)*100:.1f}%")
        print(f"   Taxa de comportamento correto: {(correct_behavior/total_tests)*100:.1f}%")
        
        # Resumo por agente
        print(f"\n🤖 RESUMO POR AGENTE:")
        for agent in self.agents:
            agent_results = [r for r in results if r["agent"] == agent]
            if agent_results:
                agent_success = sum(1 for r in agent_results if r["success"])
                agent_correct = sum(1 for r in agent_results if r["correct_behavior"])
                print(f"   {agent.upper()}: {agent_success}/{len(agent_results)} sucessos, {agent_correct}/{len(agent_results)} comportamentos corretos")
        
        # Detalhes dos problemas
        print(f"\n⚠️ PROBLEMAS DETECTADOS:")
        problems = [r for r in results if not r["correct_behavior"]]
        for problem in problems:
            print(f"   {problem['agent'].upper()}: {problem['question']}")
            print(f"      Esperado: {problem['expected_behavior']}, Atual: {problem['actual_behavior']}")
        
        # Guardrails funcionando
        print(f"\n✅ GUARDRAILS FUNCIONANDO:")
        working = [r for r in results if r["guardrails_working"] or r.get("is_guardrail_tripwire", False)]
        for work in working:
            tripwire_info = " (TRIPWIRE)" if work.get("is_guardrail_tripwire", False) else " (RESPOSTA EDUCATIVA)"
            print(f"   {work['agent'].upper()}: {work['question']}{tripwire_info}")
        
        # Detalhes dos tripwires
        tripwires = [r for r in results if r.get("is_guardrail_tripwire", False)]
        if tripwires:
            print(f"\n🚫 GUARDRAIL TRIPWIRES (Bloqueios Corretos):")
            for tripwire in tripwires:
                print(f"   {tripwire['agent'].upper()}: {tripwire['question']}")

def main():
    """Função principal - executa teste rápido por padrão"""
    tester = GuardrailsTester()
    
    # Executar teste rápido por padrão
    print("Executando teste rápido de guardrails...")
    tester.run_quick_test()

if __name__ == "__main__":
    main()