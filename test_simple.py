#!/usr/bin/env python3
"""
Script simples para testar guardrails com comandos específicos
"""

import subprocess
import sys

def test_agent(agent_name: str, question: str):
    """Testa um agente específico com uma pergunta"""
    base_dir = "/Users/arthurvaz/Desktop/Monkai/AtendentePRO"
    
    print(f"🧪 TESTANDO {agent_name.upper()} AGENT")
    print(f"❓ Pergunta: {question}")
    print("="*60)
    
    try:
        cmd = [
            "bash", "-c", 
            f"cd {base_dir} && source venv/bin/activate && echo '{question}' | python -m AtendentePro.run_env.run {agent_name}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=base_dir)
        
        print(f"📤 Código de retorno: {result.returncode}")
        print(f"📝 Saída:")
        print(result.stdout)
        
        if result.stderr:
            print(f"⚠️ Erros:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - comando demorou mais de 30 segundos")
        return False
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def main():
    """Função principal"""
    if len(sys.argv) < 3:
        print("Uso: python test_simple.py <agente> <pergunta>")
        print("Exemplo: python test_simple.py answer 'quem descobriu o brasil'")
        print("Agentes disponíveis: triage, flow, interview, answer, confirmation, knowledge, usage")
        return
    
    agent = sys.argv[1]
    question = sys.argv[2]
    
    success = test_agent(agent, question)
    
    if success:
        print("\n✅ Teste executado com sucesso!")
    else:
        print("\n❌ Teste falhou!")

if __name__ == "__main__":
    main()
